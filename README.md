# Fury Data App example project

This repository includes a functional Fury Data App: you can run an ETL, train a model and deploy it
in any scope of your application.

# Pipeline

## Execution context

- Packages included in the [requirements.txt](./requirements.txt) on the root directory, will be installed
in all the _steps_.
- You can include a *requirements.txt* within the directory of each step. In that case, it will be installed
only in that specific step (for example, if you need packages during the etl step, which are not neessary
in other steps.)

## ETL

- The `etl/etl.py` (or `etl/etl.ipynb`) program will be run during the *ETL step*. So, such file is expected to
exist.
- To persist files during the *ETL step* you must use `workspace.save_etl_file` (provided by `melitk.fda`).
  - Files persisted in such a way, will be accessible from the *LABS* and from the *Training step*.

## Training

- The `training/train.py` (or `training/train.ipynb`) program will be run during the *Training step*.
So, such file is expected to exist.
- To save a trained model you must use `workspace.save_raw_model` (provided by `melitk.fda`).
  - Such model can be later served, by building and deploying a version of the app.
- To save a metrics data you must use `workspace.save_metrics` (provided by `melitk.fda`).
  - This data will be shown in Fury's UI, in the *Training step* section.
- The saved model and metrics persisted, will be accessible from the *LABS*.
- Right now, it is not possible to persist other files during the *Training step* (it is in the backlog for the future).

## Model/Program Interface (mpi)

- the `mpi` directory contains minimal assets necessary to serve the trained model with [Osobuco](https://github.com/mercadolibre/fury_osobuco)
- If you change the model (`shared.predictor.CellChargePredictor` in this example), you may need to review
the [`bridge.py`](mpi/bridge.py) to accomodate to your new loading and predicting interface.
