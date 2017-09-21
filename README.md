# A context sensitive probabilistic model for natural language abstract syntax trees

This project aims to develop a probabilistic model for disambiguating abstract syntax trees for natural language in [Grammatical Framework](https://github.com/GrammaticalFramework/GF). The main approach involves using Expectation Maximization to estimate parameters using data from [UD-treebanks](https://github.com/UniversalDependencies).

## Running the code
To run the code you need to download the appropriate [UD-treebanks](https://github.com/UniversalDependencies) and put them in a folder named data in the project directory. You also need the GF C-runtime with python bindings installed or run the code through docker by running 'make build' to build the docker image and then 'make console' to automatically run the image and mount the needed directories. Lastly you will have to compile a GF PGF for the dictionaries for the languages you want to estimate probabilities from. Currently the code uses English, Swedish and Bulgarian to estimate probabilities.
