"""
Auteurs : Antoine Dumas (Phiméca), Michaël Baudin (EDF)

Implémente un mécanisme de mémoire cache avec sauvegarde 
et chargement depuis un fichier CSV.

TODO
----
- Implement another version based on Pickle?
"""

import openturns as ot
import os


class MemoizeWithCSVFile(ot.OpenTURNSPythonFunction):
    def __init__(
        self, function, input_cache_filename, output_cache_filename, verbose=False
    ):
        """
        Provides methods to save and load cache input and output from the ot.Function

        Parameters
        ----------
        function : openturns.Function
            The function in which the cache is loaded or saved.
        input_cache_filename : string
            Path to the input cache filename, it must be a csv file.
        output_cache_filename : string
            Path to the output cache filename, it must be a csv file.
        verbose : bool
            Set to True to print intermediate messages.
        """
        self.function_with_cache = ot.MemoizeFunction(function)
        self.input_cache_filename = input_cache_filename
        self.output_cache_filename = output_cache_filename
        self.verbose = verbose

        # Number of input/output values:
        super().__init__(function.getInputDimension(), function.getOutputDimension())
        self.setInputDescription(function.getInputDescription())
        self.setOutputDescription(function.getOutputDescription())

        try:
            self._load_cache()
        except BaseException as err:
            if self.verbose:
                print(f"Warning:", err)

    def _save_cache(self):
        """
        Save the input and output cache to a csv file.
        """
        # Get the input cache sample
        input_cache_data = self.function_with_cache.getCacheInput()
        input_cache_data.setDescription(self.getInputDescription())
        input_cache_data.exportToCSVFile(self.input_cache_filename)
        # Get the output cache sample
        output_cache_data = self.function_with_cache.getCacheOutput()
        output_cache_data.setDescription(self.getOutputDescription())
        output_cache_data.exportToCSVFile(self.output_cache_filename)

        # Print the number of saved evaluations
        if self.verbose:
            print(
                f"Saved successfully {input_cache_data.getSize()} evaluations "
                f"in {self.input_cache_filename} and {self.output_cache_filename}."
            )

    def _load_cache(self):
        """
        Load a csv file and add it to the cache of the function.
        """

        if not os.path.isfile(self.input_cache_filename) or not os.path.isfile(
            self.output_cache_filename
        ):
            raise ValueError(
                f"Cache input filename {self.input_cache_filename} or "
                f"output filename {self.output_cache_filename} not found. "
                "No evaluation loaded!"
            )
        # Load the cache from the file
        input_cache_data = ot.Sample.ImportFromCSVFile(self.input_cache_filename)
        output_cache_data = ot.Sample.ImportFromCSVFile(self.output_cache_filename)
        input_cache_size = input_cache_data.getSize()
        output_cache_size = output_cache_data.getSize()
        if input_cache_size != output_cache_size:
            raise ValueError(
                f"The input cache file {self.input_cache_filename} has "
                f"size {input_cache_size}, but the output cache file "
                f"{self.output_cache_filename} has size {output_cache_size}."
            )

        # Add the cache to the function
        if self.verbose:
            print("Adding X and Y to the cache")
            print("input_cache_data = ")
            print(input_cache_data)
            print("output_cache_data = ")
            print(output_cache_data)
        self.function_with_cache.addCacheContent(input_cache_data, output_cache_data)

        # Print the number of loaded evaluations
        if self.verbose:
            print(
                f"Loaded successfully {input_cache_data.getSize()} evaluations from "
                f"{self.input_cache_filename} and {self.output_cache_filename}."
            )

    def _exec(self, X):
        """Evaluate the model for a point :math:`X`.

        Parameters
        ----------
        X : ot.Point(input_dimension)
            Input point of dimension 4.

        Returns
        -------
        Y : ot.Point(output_dimension)
            The deviation of the beam.
        """
        # See if X in cache
        input_cache_data = self.function_with_cache.getCacheInput()
        save_cache = X not in input_cache_data
        # Evaluate Y
        Y = self.function_with_cache(X)
        # Save cache if necessary
        if save_cache:
            self._save_cache()
            if self.verbose:
                print(f"Save (X = {X}, Y = {Y}) into cache")
        else:
            if self.verbose:
                print("X already in cache")
        return Y

    def _exec_sample(self, X):
        """Evaluates a sample.
        This should not be necessary, but this avoids to create
        a list of Point."""
        X = ot.Sample(X)  # MemoryView > Sample
        # Initialize output sample
        Y = ot.Sample(0, self.getOutputDimension())

        # Evaluate the model
        for i in range(X.getSize()):
            output_point = self._exec(X[i])
            Y.add(output_point)
        return Y
