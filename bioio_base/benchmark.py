"""
    A simple benchmarking function (`benchmark()`) can be imported from
    this file to be used by individual readers to then performance test
    their individual readers
"""
import csv
import datetime
import multiprocessing
import os
import time
import tracemalloc
import typing

import psutil

import bioio_base

from .reader import Reader

OUTPUT_DESTINATION_DEFAULT = "output.csv"


class BenchmarkDefinition(typing.TypedDict):
    """
    Definition of a benchmark test
    ran on each test file, prefix is used to
    denote differences between tests
    """

    prefix: str
    test: typing.Callable[[bioio_base.types.PathLike], None]


def _all_scenes_read(
    test_file: bioio_base.types.PathLike, reader: typing.Type[Reader]
) -> None:
    """Read all scenes of the file"""
    image = reader(test_file)
    for scene in image.scenes:
        image.set_scene(scene)
        image.get_image_data()


def _all_scenes_delayed_read(
    test_file: bioio_base.types.PathLike, reader: typing.Type[Reader]
) -> None:
    """Read all scenes of the file delayed"""
    image = reader(test_file)
    for scene in image.scenes:
        image.set_scene(scene)
        image.get_image_dask_data()


def _read_ome_metadata(
    test_file: bioio_base.types.PathLike, reader: typing.Type[Reader]
) -> None:
    """Read the OME metadata of the image"""
    try:
        reader(test_file).ome_metadata
    except Exception:
        pass


def _format_bytes(num: float, suffix: str = "B") -> str:
    """Formats the bytes given into a human readable format"""
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


def benchmark_test(
    prefix: str,
    test: typing.Callable[[], None],
) -> typing.Dict[str, typing.Union[str, float]]:
    """
    Gets performance stats for calling the given function.
    Prefixes the keys of the result by the prefix given.
    """
    tracemalloc.start()
    start_time = time.perf_counter()
    test()
    end_time = time.perf_counter()
    _current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    time_elapsed = end_time - start_time
    core_usage = psutil.cpu_percent(interval=time_elapsed, percpu=True)

    time.sleep(1)  # Pause between tests
    return {
        prefix + " Time Elapsed": time_elapsed,
        prefix + " Memory Peak": _format_bytes(peak),
        prefix + " Each Core % Used": core_usage,
    }


def benchmark(
    reader: typing.Type[Reader],
    test_files: typing.List[bioio_base.types.PathLike],
    additional_test_definitions: typing.List[BenchmarkDefinition] = [],
    output_destination: str = OUTPUT_DESTINATION_DEFAULT,
) -> None:
    """Perform actual benchmark test"""
    benchmark_start_time = time.perf_counter()

    # Ensure test files are present
    assert len(test_files) > 0, "Test file list is empty"

    # Default benchmark test definitions
    default_benchmark_tests: typing.List[BenchmarkDefinition] = [
        {
            "prefix": "First Scene Read",
            "test": lambda file: reader(file).get_image_data(),
        },
        {
            "prefix": "All Scenes Read",
            "test": lambda file: _all_scenes_read(file, reader),
        },
        {
            "prefix": "First Scene Delayed Read",
            "test": lambda file: reader(file).get_image_dask_data(),
        },
        {
            "prefix": "All Scenes Delayed Read",
            "test": lambda file: _all_scenes_delayed_read(file, reader),
        },
        {
            "prefix": "Metadata Read",
            "test": lambda file: reader(file).metadata,
        },
        {
            "prefix": "OME Metadata Read",
            "test": lambda file: _read_ome_metadata(file, reader),
        },
    ]

    # Iterate the test resources capturing some performance metrics
    now_date_string = datetime.datetime.now().isoformat()
    output_rows: typing.List[typing.Dict[str, typing.Any]] = []
    test_definitions = [*default_benchmark_tests, *additional_test_definitions]
    for test_file in test_files:
        # Grab available RAM
        total_ram = psutil.virtual_memory().total

        # Use fsspec to open the file system
        fs, path = bioio_base.io.pathlike_to_fs(test_file)

        # Get file info (size, etc.)
        file_size = fs.info(path)["size"]

        # Extract file name using os.path
        file_name = os.path.basename(path)

        # Grab image interface
        image = reader(test_file)

        # Capture performance metrics
        tests_from_files: dict = {}
        for test_definition in test_definitions:
            tests_from_files = {
                **tests_from_files,
                **benchmark_test(
                    prefix=test_definition["prefix"],
                    test=lambda: test_definition["test"](test_file),
                ),
            }
        output_rows.append(
            {
                **tests_from_files,
                "File Name": file_name,
                "File Size": _format_bytes(file_size),
                "Shape": image.shape,
                "Dim Order": image.dims.order,
                "Date Recorded": now_date_string,
                "Available Memory": _format_bytes(total_ram),
                "Available CPU Cores": multiprocessing.cpu_count(),
            }
        )

    # Write out the results
    assert len(output_rows) > 0
    with open(output_destination, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=list(output_rows[0].keys()))
        writer.writeheader()
        writer.writerows(output_rows)

    benchmark_end_time = time.perf_counter()
    print(f"Performance test took {benchmark_end_time - benchmark_start_time} seconds")


def cleanup(output_destination: str = OUTPUT_DESTINATION_DEFAULT) -> None:
    if os.path.exists(output_destination):
        os.remove(output_destination)
