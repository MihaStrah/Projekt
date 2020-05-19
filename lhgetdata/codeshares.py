from getflight import getFlightCodeshares
from tryall import getAllFLightsForDay
from writetosql import writeCodeshareToSql
from gettoken import getNewToken

def getandwriteCodeshares(date):
    allids = getAllFLightsForDay(date)
    token = getNewToken()
    for iddata in allids:
        operating_id = iddata[0]
        operating_airlineid = iddata[1]
        operating_flightnumber = iddata[2]
        depscheduled = iddata[3]
        codeshares = getFlightCodeshares(token,(f"{operating_airlineid}{operating_flightnumber}"),date,4)
        for codeshare in codeshares:
            codeshare_airlineid = codeshare[0]
            codeshare_flightnumber = codeshare[1]
            writeCodeshareToSql(codeshare_airlineid, codeshare_flightnumber, operating_airlineid, operating_flightnumber, operating_id, depscheduled)
    return