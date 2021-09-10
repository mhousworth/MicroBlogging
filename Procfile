# foreman start -m gateway=1,userService=1,timelineService=3,messageService=1,searchEngineService=1
gateway: python3 -m bottle --bind=localhost:$PORT --debug --reload gateway
userService: python3 -m bottle --bind=localhost:$PORT --debug --reload userService
timelineService: python3 -m bottle --bind=localhost:$PORT --debug --reload timelineService
messageService: python3 -m bottle --bind=localhost:$PORT --debug --reload messageService
searchEngineService: python3 -m bottle --bind=localhost:$PORT --debug --reload searchEngineService
