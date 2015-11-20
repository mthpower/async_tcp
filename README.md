"Async" TCP Server
==================

Just some code I spend bodging at learning about sockets and select.

Both the client.py and server.py are Python 3.

Overall I'd say a good third of the time I spend on the problem was in reading and understanding documentation! I've never worked directly with sockets before, so it was interesting to look at something totally unfamiliar to me. I would normally like to write unit tests for this kind of thing, testing something so inherently stateful was very hard. Instead I fell back a manual approach of using the several client.py's in different console windows make sure I wasn't blocking unnecessarily. I also spent some time trying to eliminating it racing inside the main loop and using 100% of the core.
