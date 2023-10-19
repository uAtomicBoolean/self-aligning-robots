# self-aligning-robots
Robots that communicates to align themselves on a line.  
A robot both:
- send his position once per second via multicast.
- listen for any incoming message via multicast.


When receiving the position of a new robot, all the robots will re-calculate their destination.
