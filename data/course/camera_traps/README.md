# Week 1 Camera Traps teaching subset

This is a fixed, camera-disjoint teaching subset of **Caltech Camera Traps**, distributed by
[LILA BC](https://lila.science/datasets/caltech-camera-traps) under the Community Data
License Agreement—Permissive. Original image IDs, filenames, timestamps, labels, locations,
and rights holders are retained in `metadata.csv` for provenance.

The supplied AI score is the maximum animal-detection confidence from **MegaDetector
v5a.0.0 with repeat-detection elimination**, obtained from LILA BC's published results.
Caltech Camera Traps contributed to MegaDetector training; therefore this course comparison
is an illustration of evaluation structure, not an unbiased external benchmark of the model.

The subset contains complete three-frame trigger sequences. Camera locations are disjoint
across `analysis`, `holdout_camera`, and `homework_holdout`. Images are resized to at most
640 pixels on a side for direct individual-file download from GitHub.

The subset is deliberately small and balanced for teaching. It is not a probability sample
of all Caltech Camera Traps images, camera locations, ecosystems, or wildlife cameras.
See `release_summary.json` for frozen denominators and descriptive results.
