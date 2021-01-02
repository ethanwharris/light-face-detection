import pytorch_lightning as pl
import mypackage
from typing import Dict
import argparse
import yaml

def load_yaml_file(yaml_path:str) -> Dict:
    with open(yaml_path,"r") as foo:
        return yaml.load(foo, Loader=yaml.FullLoader)

def parse_arguments() -> Dict:
    ap = argparse.ArgumentParser()

    ap.add_argument("--yaml", "-y", type=load_yaml_file, required=True, help="configuration yaml path for training")
    # TODO add resume
    return ap.parse_args()

def main(kwargs:Dict):
    arch = kwargs['arch']
    config = kwargs['config']
    hparams = kwargs['hparams']
    in_channels = kwargs['in_channels']

    datamodule = kwargs['datamodule']
    trainer_configs = kwargs['trainer']

    checkpoint_dirpath = kwargs['checkpoint']['dirpath']
    checkpoint_verbose = kwargs['checkpoint'].get('verbose', True)
    checkpoint_filename = kwargs['checkpoint']['filename']
    checkpoint_monitor = kwargs['checkpoint']['monitor']
    checkpoint_save_top_k = kwargs['checkpoint']['save_top_k']
    checkpoint_mode = kwargs['checkpoint']['mode']

    model = mypackage.module.build(arch, config, hparams=hparams,
        num_classes=1, in_channels=in_channels)

    dm = mypackage.datamodule.WiderFaceDataModule(
        partitions=datamodule['partitions'],
        train_kwargs=datamodule['train'],
        val_kwargs=datamodule['val'])

    checkpoint_callback = pl.callbacks.ModelCheckpoint(
        dirpath= checkpoint_dirpath,
        verbose= checkpoint_verbose,
        filename=checkpoint_filename.format(
            arch=arch, config=config,
            dataset=datamodule['dataset']),

        monitor=checkpoint_monitor,
        save_top_k=checkpoint_save_top_k,
        mode=checkpoint_mode
    )

    trainer = pl.Trainer(
        gpus=trainer_configs.get('gpus',1),
        accumulate_grad_batches=trainer_configs.get('accumulate_grad_batches',1),
        resume_from_checkpoint=None, # TODO handle here
        checkpoint_callback=checkpoint_callback,
        max_epochs=trainer_configs.get('max_epochs', 100),
        check_val_every_n_epoch=trainer_configs.get('check_val_every_n_epoch', 1),
        precision=trainer_configs.get('precision', 32),
        gradient_clip_val=trainer_configs.get('gradient_clip_val', 0))

    trainer.fit(model, dm)

if __name__ == "__main__":
    args = parse_arguments()
    main(args.yaml)
