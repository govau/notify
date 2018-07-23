# expedition results

## Existing Python API
The existing python API is lacking a bit with regards to discoverability around what endpoints the api exposes, and what the rough ‘schema’ of each endpoint is.

The rough approach I took was to look through [admin/notify-client](https://github.com/govau/notifications/tree/master/admin/app/notify_client) stubs to see what was being accessed by admin. [Here’s](https://github.com/govau/notifications/blob/19c97b6a0fcd253d71f3bd11f0b1068a1e0dc1a3/admin/app/notify_client/service_api_client.py#L66) an example of where notify-admin gets all the services. Obviously you can’t really see much about what gets exposed through that API, what parameters it might expect, or what errors might get returned. Bleh.

So the next step was to sift through notify-api and see what gets spat out. Each “domain” has a `rest.py` file that exposes stuff about that resource. [Here’s the corresponding service endpoint](https://github.com/govau/notifications/blob/master/api/app/service/rest.py#L133). You can see there that the endpoint accepts parameters like `user_id` to get the services specific to a user. This is pretty useful but only really observable by visiting each endpoint one-by-one and checking what arguments are pulled, and the logic around how they’re used.

I had a bit more hope around doing any of this systematically when I saw mentions of “schema”. [schema.py](https://github.com/govau/notifications/blob/master/api/app/schemas.py) is so close to being useful; but for whatever reason they went with a blacklist instead of a whitelist approach to things. For each model in the database, they blacklist certain fields from being exposed, rather than whitelisting the fields they want to be dumped out. So instead of just looking at the schema, you have to look at the model; get an idea of what’s there and then mentally remove the blacklisted parts as defined in schema.py. Not entirely useful.

In practice, what I found myself doing was as follows:

* look at the page we’re trying to build
* think about what the data backing it would be
* find that stub + endpoint in admin/notify-client
* find the corresponding endpoint in `api/*/rest.py` and see what params it accepts
* check the model + schema for it to get an idea of what is available
* [write a test program that calls it with various input](https://github.com/govau/notifications/blob/api-expedition/api-wrappers/python-api/interact.py), capture the output, and craft that into a type in our protobuf schema


### Moving forward

I suggest that we pull back as much as possible from any python API  “bespoke” endpoints, and just wrap the most general ones necessary to graph traversal.

# gRPC
While I have some initial concerns about gRPC and HTTP/2 (hundreds of GitHub issues, performance questions); I found that the time to get a service up-and-running is pretty great. Within hours we had a gRPC backend proxying requests to the python API; and a GraphQL server acting as a gRPC client. 

There’s a certain amount of boilerplate necessary in mapping the python API results into what the gRPC protobuf schema expects. This isn’t particularly fun in go. I would prefer to write a declarative set of transformation descriptions rather than an iterative set of instructions for how to do that conversion. Any language that would give us that sort of power would be very unlikely to support gRPC, protobuf, run nicely on CF, etc. It’s a reasonable tradeoff to make.

As a whole, gRPC seems like it would suit our purposes nicely. Being able to access it from node in about 5 seconds was a great experience.

That said, Twirp would likely hit most of these points as well. Locking ourselves out of streaming could be a bummer though.

# GraphQL
I started the expedition by writing our GraphQL server in Go. While graph-gophers/graphql-go provided what was the lightest-weight graphql option, it was still an annoying amount of boilerplate to get things up and going. At this point we were defining types for our third time. (python-api decoder, generated grpc, protobuf stubs, now graphql resolvers). This would have been less problematic if the graphql library didn’t require methods for every exposed field.

The feedback loop was also more irritating; because of the heavy use of reflection by the library. gRPC would generate stubs that would fail to compile if interfaces weren’t implemented correctly. GraphQL would instead panic at runtime if the resolvers weren’t implemented quite right. 

The library also required a confusing amount of pointers to be returned from resolvers, in places that didn’t feel natural. In short, what felt appropriate or acceptable on the gRPC side of things, felt like a pain here. Going from typed gRPC -> typed GraphQL felt as/more painful than untyped python-api -> typed gRPC.

## Node
Just as a sense-check, I wrote a quick apollo-server  GraphQL server in Node that called the gRPC client. This was important because it validated that gRPC was useful in a cross-language sense. It worked great, and the apollo server was up and running in short order. Then resolvers were much more natural to write, and the tooling felt like it was at the right spot.

I have a small amount of hesitation, purely around failing silently/at runtime where fields are missing.  The saving grace here is that the GraphQL layer will save us from sending garbage to clients (i.e. won’t let us send an object where an int is expected). Our contract can never be broken, but we might not know immediately when something isn’t quite being resolved correctly.

## Overall
I’m almost entirely convinced that GraphQL is a fundamental part of any frontend we build going forward. Talking through some issues that might arise and how we would address them convinced me that ongoing development would be drastically easier with a GraphQL layer for our frontend to call on. Doing it in Node is likely to get us there quickly and without much to change if anything isn’t quite right.


# Conclusion
For the frontend, GraphQL in Node seems to be the way to go. It’s going to pay for itself multiple times over as we continue development. It also benefits massively from a strong RPC backend option. Half the reason this server was so thin and simple is because so much of the pain was already taken away by gRPC.

On the backend, implementing a gRPC (or any RPC) server is going to be a bit annoying in Go, but I feel most of that pain comes from wrangling an untyped, undocumented, untooled API into something much more specific. gRPC makes sense for now for it’s ubiquity and ease-of-integration. The pain of typing notify-api should be paid off fairly quickly by the time saved writing and maintaining the many client libraries we’ll need to deal with, including the GraphQL server.
