# API expedition
## How might we continue development of Notify in a way that leverages our strengths?

The notify API is a solid foundation to build on, and is worth maintaining and extending; however python is not our strength, and we have no long-running knowledge of the existing system.

One approach is to modify it as little as possible for our purposes. The less we drift from GDS’s source, the more likely it is that we will be able to pull in bug fixes and features.  Under this approach, any larger features or enhancements we want to build out would need to be done elsewhere and stitched together through some wrapper.

This directory explores some options for how we might maintain the stable notify python API; while allowing further feature development in more rapidly developed external backend. They should all be exposed in a way that allows us to utilise our existing react components and design system. In this way we might incrementally adjust the frontend while transitioning to  more of a DTA supported stack.

## How to use this repository
This is more of a collection of snippets, than a fully realised system. As such, setup and running it is fairly ad-hoc.

Each directory has a minimal makefile that contains a `setup` and `run` directive. Read through these to understand what they’re going to install on your system when you call `make setup`.

### gRPC backend

You’ll need to have notify-api running in the background. After that, you should go into the [grpc](https://github.com/govau/notifications/tree/api-expedition/api-wrappers/grpc) directory, type `make setup`, and `make run`  to get our Go gRPC backend running.  Check the code there to see how we authenticate to the python API, and how we implement the protobuf spec.

This spec is located in grpc_defs_notify.proto. 

### Node GraphQL

Check out the code here to see how we define a GraphQL schema and proxy requests using a gRPC client. 

## Go GraphQL
A very rudimentary GraphQL server showing how awkward it is to write a GraphQL server in Go.

## python-api
[interact.py](https://github.com/govau/notifications/blob/api-expedition/api-wrappers/python-api/interact.py) is a simple script that lets us dump out responses from the python notify-api so that we can base types on them.
