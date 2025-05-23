"""
    A simple benchmarking function (`benchmark()`) can be imported from
    this file to be used by individual readers to then performance test
    their individual readers
"""
import csv
import datetime
import multiprocessing
import pathlib
import time
import tracemalloc
import typing

import psutil

from .reader import Reader


def _all_scenes_read(reader: typing.Type[Reader], test_file: pathlib.Path) -> None:
    """Read all scenes of the file"""
    image = reader(test_file)
    for scene in image.scenes:
        image.set_scene(scene)
        image.get_image_data()


def _all_scenes_delayed_read(
    reader: typing.Type[Reader], test_file: pathlib.Path
) -> None:
    """Read all scenes of the file delayed"""
    image = reader(test_file)
    for scene in image.scenes:
        image.set_scene(scene)
        image.get_image_dask_data()


def _read_ome_metadata(reader: typing.Type[Reader], test_file: pathlib.Path) -> None:
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


def _benchmark_function(
    prefix: str, fn: typing.Callable
) -> typing.Dict[str, typing.Union[str, float]]:
    """
    Gets performance stats for calling the given function.
    Prefixes the keys of the result by the prefix given.
    """
    tracemalloc.start()
    start_time = time.perf_counter()
    fn()
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


def benchmark(reader: typing.Type[Reader], test_file_dir: pathlib.Path) -> None:
    """Perform actual benchmark test"""
    benchmark_start_time = time.perf_counter()

    # Ensure test files are present
    assert (
        test_file_dir.exists()
    ), f"Test resources directory can't be found: {test_file_dir}"
    assert any(
        test_file_dir.iterdir()
    ), f"Test resources directory is empty: {test_file_dir}"

    # Iterate the test resources capturing some performance metrics
    now_date_string = datetime.datetime.now().isoformat()
    output_rows: typing.List[typing.Dict[str, typing.Any]] = []
    for test_file in test_file_dir.iterdir():
        test_file = pathlib.Path(test_file)

        # Grab available RAM
        total_ram = psutil.virtual_memory().total

        # Grab image interface
        image = reader(test_file)

        # Capture performance metrics
        # TODO: Consider just printing?
        output_rows.append(
            {
                **_benchmark_function(
                    prefix="First Scene Read",
                    fn=lambda: reader(test_file).get_image_data(),
                ),
                **_benchmark_function(
                    prefix="All Scenes Read",
                    fn=lambda: _all_scenes_read(reader, test_file),
                ),
                **_benchmark_function(
                    prefix="First Scene Delayed Read",
                    fn=lambda: reader(test_file).get_image_dask_data(),
                ),
                **_benchmark_function(
                    prefix="All Scenes Delayed Read",
                    fn=lambda: _all_scenes_delayed_read(reader, test_file),
                ),
                **_benchmark_function(
                    prefix="Metadata Read",
                    fn=lambda: reader(test_file).metadata,
                ),
                **_benchmark_function(
                    prefix="OME Metadata Read",
                    fn=lambda: _read_ome_metadata(reader, test_file),
                ),
                "File Name": test_file.name,
                "File Size": _format_bytes(test_file.stat().st_size),
                "Shape": image.shape,
                "Dim Order": image.dims.order,
                "Date Recorded": now_date_string,
                "Available Memory": _format_bytes(total_ram),
                "Available CPU Cores": multiprocessing.cpu_count(),
            }
        )

    # Write out the results
    assert len(output_rows) > 0
    with open("output.csv", "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=list(output_rows[0].keys()))
        writer.writeheader()
        writer.writerows(output_rows)

    benchmark_end_time = time.perf_counter()
    print(f"Performance test took {benchmark_end_time - benchmark_start_time} seconds")
