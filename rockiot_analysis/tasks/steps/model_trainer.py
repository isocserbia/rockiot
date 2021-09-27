import os
import pickle

import pandas as pd

from luminaire.optimization.hyperparameter_optimization import HyperparameterOptimization
from luminaire.exploration.data_exploration import DataExploration

from luminaire.model.base_model import BaseModelObject
from luminaire.model.lad_filtering import LADFilteringModel

from celery.utils.log import get_task_logger

from tasks.steps.config import sensors

logger = get_task_logger(__name__)


def train_models(devices_dict):
    trained_models = 0
    for k, v in devices_dict.items():
        for s in sensors:
            values = v[s]
            if values and len(values) > 0:
                # print(f'Loaded values {values}')
                # original_data = pd.DataFrame.from_records(values).set_index('index')
                training_data = pd.DataFrame.from_records(values).set_index('index')
                # hopt_obj = HyperparameterOptimization(freq='D')
                # opt_config = hopt_obj.run(data=original_data)
                # de_obj = DataExploration(freq='D', **opt_config)
                # training_data, pre_prc = de_obj.profile(original_data)
                training_model = LADFilteringModel(hyper_params={"is_log_transformed": 0}, freq='H')
                data_summary = {
                    'ts_start': training_data.first_valid_index(),
                    'ts_end': training_data.last_valid_index(),
                    'is_log_transformed': False,
                }
                success, model_date, model = training_model.train(data=training_data, **data_summary)

                if success:
                    path = f'/data/analysis_{k}_{s}.model'
                    file = open(path, 'wb')
                    model_json = pickle.dumps(model)
                    file.write(model_json)
                    file.close()
                    logger.info(f'Model created {k} / {s}. Date {model_date}, File path: {path}')
                    trained_models += 1
                else:
                    logger.debug(f"Model {k} / {s} failed.")

    return trained_models
