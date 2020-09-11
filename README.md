Greendeck Python Assignment


## General Approach:

A single endpoint is created that will handle all queries.
It first validates the input json format.

Then it checks for any filters present in the query,
and applies each filter one by one on the data.

Then, it checks each query type present in the query,
and calculates and adds the field to the response dictionary.

Finally it sends the response as a JSON.


## Filtering:

For filtering by discount, brand name, etc.
it uses the apply function to obtain each row value
and applies the condition on each row respectively
