# Idea
The one thing I was thinking about when working on creating domain models in the lab was to have a visualization of how the uml looks like at the current time. Just something quick to make sure that I am doing everything correctly. What would have been useful for me is an easy way to just plot the domain model using some graphing tool. e.g., domain_model.plot() or domain_model.write_image(<path>).

This repository shows an implementation of how this function could look like in a practical setting. For now, it is simply named "model_to_image".

# Dependency note
In addition to the besser dependency, this solution also requires the python graphviz package and for graphviz to be installed directly on the main system to render it. See more information on which dependencies were used for the following examples in `requirements.txt`

# Examples
Here are a few examples of a library example that I used for testing the function each with different layout engines:

## Dot
![Screenshot of dot layout example](/Library_model_dot.png)

## Neato
![Screenshot of neato layout example](/Library_model_neato.png)
