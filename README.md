# sdlc-project- EventMaster

Prerequisites:

For both downloads do normal setup, then start docker desktop and make sure its running throughout setup.
Download git here: https://git-scm.com/downloads
Download Docker here: https://www.docker.com/products/docker-desktop/

1. In command prompt type git clone https://github.com/Arvinmoradi-ui/sdlc-practice
2. In command prompt type cd sdlc-practice
3. In the sdlc-practice folder type: docker build -t eventmaster-app .
4. Next in the same folder after things have been downloaded type: docker run -p 5000:5000 eventmaster-app
5. Then open any browser and go to http://127.0.0.1:5000 
