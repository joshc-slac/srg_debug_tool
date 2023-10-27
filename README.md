# SRGTester
This codebase is designed to provide procedural and iterable mechansims to debug the multi-year issues facing, nominally, the spherical rotor gauge on the GMD and the issues surrounding its serial interface. 

Ideally this codebase is also extensible to future problems of a similar form. Expressed generally as:
>This codebase presents a mechanism to schedule and execute tasks needed to perturb and monitor various tools in our EPICS control stack. 
> What if we could procedurably schedule PVs to be perturbed and catalog various sources of truth that change in response to that pertubation? This might seem trivially but especially when not done in an ad-hoc manner this is an exceptionally tractable path for debugging sufficiently complex software projects. 


## Development
### Setup
- required: `python3`, `make`, `rsync`*
- see `requirements.txt` for specific python packages 
- Running `make setup`, `source bin/activate`, `pip3 install -r requirements.txt` should be sufficient to complete setup

### Runtime
- `make run` will launch SRGTester server 
- `make request_reading` will spawn a client session that will request the server perform a reading

To run on our production tooling I rsync the relevant contents of this folder to our "build" machine:
`rsync -zvaP *.py *.txt Makefile [username]@psbuild-rhel7:~/[whatever you want to name the folder]`

You will have to run `make setup && source bin/activate && pip3 install -r requirements.txt` on the production device as well. In the future you would only have to source the python environment. 

*You can also use our "git as a file transfer protocol" schema that we use elsewhere, I suggest disambiguating the wonderful tool that is git from ftp.*

### Makefile
To simplify the user interactions we are codifying normal steps in the Makefile. 
- `make setup` - will add python venv infrastructure to current directory if not already present
- `make run` - runs the "application" of this repo: SRGTester, waits for requested action from client
- `make request_reading`- spawns an instance of the client and specifically requests a reading be performed by server
- `make transfer_working_files` - rsyncs working files to development machine `psbuild-rhel7`, if FTPUSER not definded defaults to `joshc`
- `make flake8` - will lint the project, please do so!

Pedantic note: this should all be dockerized why wont they let me run docker on prod tools.

## Note that no besides Josh cares about
This would all be a million times better in gods programming langauge c++ todo port 
### TODOS:
- [ ] integrate flake8 into make file

- [ ] make TCP server more legit or switch to GRPC (or just protobuf over tcp...)
- [ ] Formalize (as far as python allows) notion of job queue, what is a job in python? Potentially use a python "wrapper" to anonymize these functions for job queue purposes
- [ ] add spdlog or our epics logging environment
- [ ] Formalize / unify pyepics interactions to be consistent with the rest of our codebase (if that consistency exists)
- [ ] Mourn at the alter of c++ i will return just you wait
