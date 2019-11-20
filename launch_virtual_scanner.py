import argparse
import os
from os.path import join, basename, relpath, dirname, exists
import glob
import joblib
from joblib import Parallel, delayed
from collections import defaultdict
import numpy as np
from easydict import EasyDict


def sample_instance(instance_path, virtualscan):
    path = "/".join(instance_path.split(sep='/')[:-3])
    category = instance_path.split(sep='/')[-3]
    instance_name = instance_path.split(sep='/')[-2]
    ply_path = join(path, "ply", category)
    if not exists(ply_path):
        os.makedirs(ply_path)
    out_path = join(ply_path, instance_name + ".points.ply")
    command = virtualscan + " " + instance_path + " 10"
    print(instance_path[:-3] + "ply", out_path, "\n")
    if not exists(out_path):
        os.system(command)
        os.rename(instance_path[:-3] + "ply", out_path)

def shoot_rays(args):
    classes = [x for x in next(os.walk(args.input))[1]]
    for obj_class in classes:
        ply_path = join(args.input, "ply", obj_class)
        if not exists(ply_path):
            os.makedirs(ply_path)
        obj_instances = sorted([x for x in next(os.walk(join(args.input, obj_class)))[1] if "ply" not in x])
        # obj_instances = obj_instances[:min(200, len(obj_instances))]  # Keep 200 first
        class BatchCompletionCallBack(object):
            completed = defaultdict(int)
            def __init__(self, time, index, parallel):
                self.index = index
                self.parallel = parallel
            def __call__(self, index):
                BatchCompletionCallBack.completed[self.parallel] += 1
                print("Progress : %s %% " %
                      str(BatchCompletionCallBack.completed[self.parallel] * 100 / len(obj_instances)))
                if self.parallel._original_iterator is not None:
                    self.parallel.dispatch_next()
        joblib.parallel.BatchCompletionCallBack = BatchCompletionCallBack
        instance_paths = [join(args.input, obj_class, obj_instance, "model.obj")
                          for obj_instance in obj_instances]
        if np.any(["03797390/ply/model" in x for x in instance_paths]):
            print("Debug")
        _ = Parallel(n_jobs=-1, backend="multiprocessing") \
            (delayed(sample_instance)(*i) for i in zip(instance_paths, [args.virtualscan] * len(instance_paths)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, help='Input folder', required=True)
    parser.add_argument('--virtualscan', type=str, help='Path to the virtual scanner executable', default='virtual_scanner/build/virtualscanner')
    args = parser.parse_args()
    shoot_rays(EasyDict(args.__dict__))


if __name__ == '__main__':
    main()
