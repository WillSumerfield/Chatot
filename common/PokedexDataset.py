"""This file contains a Huggingface class definition for our dataset."""

import datasets
import json


_DESCRIPTION = """\
A Dataset Containing the Pokedex entries of all 151 of the original pokemon.
"""


class PokedexDatasetConfig(datasets.BuilderConfig):
    """BuilderConfig for the PokedexDataset."""

    def __init__(self, **kwargs):
        """BuilderConfig for SQUAD.
        Args:
          **kwargs: keyword arguments forwarded to super.
        """
        super(PokedexDatasetConfig, self).__init__(**kwargs)


class PokedexDataset(datasets.GeneratorBasedBuilder):
    """Based on the SQUAD Dataset Generator"""

    BUILDER_CONFIGS = [
        PokedexDatasetConfig(
            name="plain_text",
            version=datasets.Version("1.0.0", ""),
            description="Plain text",
        ),
    ]

    def _info(self):
        return datasets.DatasetInfo(
            description=_DESCRIPTION,
            features=datasets.Features(
                {
                    "text": datasets.Value("string")
                }
            ),
            # No default supervised_keys (as we have to pass both question
            # and context as input).
            supervised_keys=None
        )

    def _split_generators(self, dl_manager):
        """Return a train-test split"""
        return [
            datasets.SplitGenerator(name=datasets.Split.TRAIN, gen_kwargs={"filepath": "dataset/train_dataset.json"}),
            datasets.SplitGenerator(name=datasets.Split.TEST, gen_kwargs={"filepath": "dataset/test_dataset.json"}),
        ]

    def _generate_examples(self, filepath):
        """This function returns the examples in the raw (text) form."""

        # Store the entry index
        key = 0

        # Open the file
        with open(filepath, encoding="utf-8") as f:

            # Load the entries as a list
            entries = json.load(f)

            # For every entry, yield an example
            for entry in entries:
                print(entry)
                yield key, {"text": entry}
                key += 1
