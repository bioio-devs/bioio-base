#!/usr/bin/env python
import csv
import pathlib

import bioio_base.benchmark
import bioio_base.noop_reader


def test_benchmark_local_file() -> None:
    # Arrange
    temp_file = pathlib.Path("temp_file.txt")
    try:
        temp_file.write_text("This is a temporary file for testing purposes.")
        bioio_base.benchmark.benchmark(bioio_base.noop_reader.NoopReader, [temp_file])

        # Act
        output_destination = pathlib.Path("output.csv")

        # Assert: Run some simple asserts to check output exists
        output_destination = pathlib.Path("output.csv")
        assert output_destination.exists(), "Output file was not created"
        assert output_destination.stat().st_size > 0, "Output file is empty"
        with open(output_destination, "r") as csvfile:
            csv_reader = csv.DictReader(csvfile)
            first_test = next(csv_reader)
            assert first_test["File Name"] == "temp_file.txt"
            assert first_test["File Size"] == "46.0B"
    finally:
        temp_file.unlink(missing_ok=True)
        bioio_base.benchmark.cleanup()


def test_benchmark_http_file() -> None:
    try:
        # Arrange
        http_file = "https://gettylargeimages.s3.amazonaws.com/00094701.jpg"

        # Act
        bioio_base.benchmark.benchmark(bioio_base.noop_reader.NoopReader, [http_file])

        # Assert: Run some simple asserts to check output exists
        output_destination = pathlib.Path("output.csv")
        assert output_destination.exists(), "Output file was not created"
        assert output_destination.stat().st_size > 0, "Output file is empty"
        with open(output_destination, "r") as csvfile:
            csv_reader = csv.DictReader(csvfile)
            first_test = next(csv_reader)
            assert first_test["File Name"] == "00094701.jpg"
            assert first_test["File Size"] == "26.9MiB"
    finally:
        bioio_base.benchmark.cleanup()
