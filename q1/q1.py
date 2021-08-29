#!/usr/bin/env python
from datetime import datetime
from bisect import bisect
import os, logging, json, re, sys

### Configurations ###
TIME_FORMAT="%d/%b/%Y:%H:%M:%S %z"
BAN_RULES=[
    {"hitCount": 40, "timeRange": 60, "banInterval": 600},
    {"hitCount": 100, "timeRange": 600, "banInterval": 3600},
    {"hitCount": 20, "timeRange": 600, "banInterval": 7200, "reqestFilter": r' /login '}
]
### End ###

DEBUG = int(os.getenv('DEBUG', 0))
if DEBUG == 0:
    dbg_lvl = logging.INFO
else:
    dbg_lvl = logging.DEBUG
LOG_CFG = {
    "level": dbg_lvl,
    "datefmt": '%Y-%m-%d %H:%M:%S',
    "format": '%(asctime)s [%(levelname)s] %(module)s.%(funcName)s: %(message)s'
}
logging.basicConfig(level=LOG_CFG["level"],datefmt=LOG_CFG["datefmt"],format=LOG_CFG["format"])

def usage():
    print(f'Usage: {sys.argv[0]} <ApacheLogFile>', flush=True)

def loadRules(banRules=BAN_RULES):
    rlist = []
    for r in banRules:
        if "reqestFilter" in r:
            rlist.append(Rule(r["timeRange"], r["hitCount"], r["banInterval"], r["reqestFilter"]))
        else:
            rlist.append(Rule(r["timeRange"], r["hitCount"], r["banInterval"]))
    return rlist


class Rule:
    def __init__(self, timeRange, hitCount, banInterval, reqestFilter=None):
        self.timeRange = timeRange
        self.hitCount = hitCount
        self.reqestFilter = reqestFilter
        self.banInterval = banInterval

    def hit(self, logEntry):
        if self.reqestFilter:
            if re.search(self.reqestFilter, logEntry["request"]):
                return True
            else:
                return False
        return True

    def discardExpire(self, queue, now):
        expireAt = now - self.timeRange
        while len(queue) > 0 and queue[0]["time"] <= expireAt:
            queue.pop(0)

    def banCheck(self, queue, now):
        self.discardExpire(queue, now)
        #logging.debug(json.dumps(queue))
        if len(queue) >= self.hitCount:
            return self.banInterval
        return None

class LogProcessor:
    def __init__(self, rules, tmFmt=TIME_FORMAT):
        self.rules = rules
        self.tmFmt = tmFmt
        self.logs = []
        self.logQs = {}
        self.lnBuff = []
        self.unbanCmds = []
        self.banned = []
        self.lineCount = 0
        logging.debug(json.dumps({'rulesCount': len(self.rules)}))
        
    def popValue(self):
        val = self.lnBuff.pop(0)
        if val:
            if re.search(r'^["\'\[]', val) and not re.search(r'["\'\]]$', val):
                while not re.search(r'["\'\]]$', self.lnBuff[0]):
                    val += " " + self.lnBuff.pop(0)
                val += " " + self.lnBuff.pop(0)
        return val
        
    def lineFeed(self, ln):
        self.lnBuff = ln.strip().split()
        self.lineCount += 1
        #logging.debug(len(self.lnBuff))
        if len(self.lnBuff) > 8:
            #logging.debug("{:08}# {}".format(self.lineCount, ln.strip()))
            logEntry = {
                "remote": self.popValue(),
                "identd": self.popValue(),
                "user": self.popValue(),
                "time": int(datetime.strptime(self.popValue()[1:-1], self.tmFmt).timestamp()),
                "request": self.popValue()[1:-1],
                "status": self.popValue(),
                "size": self.popValue(),
                "referer": self.popValue()[1:-1],
                "userAgent": self.popValue()[1:-1]
            }
            logging.debug(json.dumps({'lnNum': self.lineCount, 'content': ln.strip(), 'timestamp': logEntry["time"]}))
            #if logEntry["remote"] not in self.banneds:
            self.appendLog(logEntry)

    def appendLog(self, log):
        now = log["time"]
        src = log["remote"]
        #logging.debug(json.dumps({'now': now}))
        #self.logs.append(log)
        if src not in self.logQs:    
            self.logQs[src] = self.initQueues()
        rqs = self.logQs[src]
        maxBanInt = 0
        for i, r in enumerate(self.rules):
            if r.hit(log):
                #logging.debug("hit - rule[{}]/{}".format(i, json.dumps({"time": log["time"], "request": log["request"]})))
                rqs[i].append({"time": log["time"], "request": log["request"]})
                #logging.debug(json.dumps(rqs[i]))
                banInt = r.banCheck(rqs[i], now)
                if banInt and banInt > maxBanInt:
                    maxBanInt = banInt
        logging.debug(json.dumps({'maxBanInt': maxBanInt}))
        if maxBanInt > 0:
            self.ban(src, now+maxBanInt+1, now)
        logging.debug(json.dumps({"remote": src, "queueLens": [len(self.logQs[src][0]), len(self.logQs[src][1]), len(self.logQs[src][2])]}))
        for i in range(len(self.logQs[src])):
            logging.debug(json.dumps({f'{src}.rule{i}': self.logQs[src][i]}))
        logging.debug(json.dumps({"banned": self.banned}))

    def initQueues(self):
        queues = []
        for r in self.rules:
            queues.append([])
        return queues

    def ban(self, remote, expireAt, now):
        c = self.unbanExpired(now)
        logging.debug(json.dumps({'unbanned': c}))
        i = self.banPush(remote, expireAt, now)
        logging.debug(json.dumps({'bannedIndex': i}))

    def banPush(self, remote, expireAt, now):
        isBanned = False
        inserted = False
        if len(self.banned) == 0:
            self.banAct(remote, now)
            self.banned.append({"expireAt": expireAt, "remote": remote})
            return 0
        for i, b in enumerate(self.banned):
            if b["remote"] == remote:
                isBanned = True
                if expireAt <= b["expireAt"]:
                    inserted = True
                else:
                    self.banned.pop(i)
                break
        if not isBanned:
            self.banAct(remote, now)
        if inserted:
            return i
        if len(self.banned) == 0:
            self.banned.append({"expireAt": expireAt, "remote": remote})
            return 0
        for i, b in enumerate(self.banned):
            if expireAt <= b["expireAt"]:
                self.banned.insert(i, {"expireAt": expireAt, "remote": remote})
                return i
        self.banned.append({"expireAt": expireAt, "remote": remote})
        return len(self.banned)-1

    def unbanExpired(self, now):
        c = 0
        if len(self.banned) == 0:
            return c
        while len(self.banned) > 0 and self.banned[0]["expireAt"] <= now:
            entry = self.banned.pop(0)
            self.unbanAct(entry["remote"], entry["expireAt"])
            c += 1
        return c

    def unbanAll(self):
        while len(self.banned) > 0:
            entry = self.banned.pop(0)
            self.unbanAct(entry["remote"], entry["expireAt"])

    def banAct(self, remote, time):
        logging.debug(f'{time},BAN,{remote}')
        print(f'{time},BAN,{remote}', flush=True)
        
    def unbanAct(self, remote, time):
        logging.debug(f'{time},UNBAN,{remote}')
        print(f'{time},UNBAN,{remote}', flush=True)

#main
if len(sys.argv) < 2:
    print(f'ERROR: missing log file argument.', flush=True)
    usage()
    exit(1)
logFile = sys.argv[1].strip()
lp = LogProcessor(loadRules())
with open(logFile, "r") as f:
    while True:
        ln = f.readline();
        if not ln:
            break
        lp.lineFeed(ln)
lp.unbanAll()
