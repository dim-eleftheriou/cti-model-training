import os
import shutil

data_path = "C:/Users/eleftheriou/Desktop/llm_training_dataset/text_completion/opencti"
files_list = os.listdir(data_path)
files_dict = {name:os.path.getsize(os.path.join(data_path, name)) for name in files_list}
files_dict = {k: v for k, v in sorted(files_dict.items(), key=lambda item: item[1])}

save_path = "C:/Users/eleftheriou/Desktop/train_data/llm_batched_data"
i = 1
batch_size = len(files_dict) / 5 + len(files_dict) % 5
save_dir = os.path.join(save_path, f"batch_{i}")
os.mkdir(save_dir)

for f, s in files_dict.items():
    save_dir_length = len(os.listdir(save_dir))
    if save_dir_length <= batch_size:
        shutil.copyfile(os.path.join(data_path, f), 
                        os.path.join(save_path, f"batch_{i}", f))
    else:
        i += 1
        save_dir = os.path.join(save_path, f"batch_{i}")
        os.mkdir(os.path.join(save_path, f"batch_{i}"))
        shutil.copyfile(os.path.join(data_path, f), 
                        os.path.join(save_path, f"batch_{i}", f))
        
        
