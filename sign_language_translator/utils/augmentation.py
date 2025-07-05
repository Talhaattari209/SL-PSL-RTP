import os
import pickle
import numpy as np
from pathlib import Path
import pandas as pd
import logging
from scipy.interpolate import interp1d
from scipy.ndimage import gaussian_filter1d

# --- AUGMENTATION ---
def augment_landmarks(landmarks, rotation_angle=10, scale_factor=1.1, noise_std=0.01, frame_drop_prob=0.1):
    augmented = landmarks.copy()
    frames, keypoints, coords = augmented.shape
    theta = np.radians(np.random.uniform(-rotation_angle, rotation_angle))
    rotation_matrix = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
    scale = np.random.uniform(0.9, scale_factor)
    xy = augmented[:, :, :2]
    xy = np.dot(xy, rotation_matrix) * scale
    augmented[:, :, :2] = xy
    augmented += np.random.normal(0, noise_std, augmented.shape)
    keep_mask = np.random.uniform(0, 1, frames) > frame_drop_prob
    if keep_mask.sum() > 0:
        augmented = augmented[keep_mask]
        if len(augmented) < frames:
            pad_size = frames - len(augmented)
            augmented = np.pad(augmented, ((0, pad_size), (0, 0), (0, 0)), mode='edge')
    else:
        random_frame = augmented[np.random.randint(frames)][None, :, :]
        augmented = np.repeat(random_frame, frames, axis=0)
    return augmented

def augment_complete_to_all(landmark_dir, dataset_csv, num_augmentations_per_source=4):
    landmark_dir = Path(landmark_dir)
    try:
        dataset = pd.read_csv(dataset_csv)
        if not set(['video_name', 'label']).issubset(dataset.columns):
            raise ValueError(f"Expected columns 'video_name' and 'label' in {dataset_csv}, found: {list(dataset.columns)}")
        logging.info(f"Loaded dataset from {dataset_csv} with {len(dataset)} entries")
    except Exception as e:
        logging.error(f"Failed to load {dataset_csv}: {e}")
        return
    sources = []
    for index, row in dataset.iterrows():
        video_name = row['video_name']
        label = row['label'].lower()
        folder_path = landmark_dir / video_name
        complete_pkl = folder_path / 'landmarks_complete.pkl'
        if complete_pkl.exists():
            sources.append((video_name, label))
    if not sources:
        logging.error("No sources with landmarks_complete.pkl found")
        return
    targets = []
    for index, row in dataset.iterrows():
        video_name = row['video_name']
        label = row['label'].lower()
        folder_path = landmark_dir / video_name
        complete_pkl = folder_path / 'landmarks_complete.pkl'
        if not complete_pkl.exists() and video_name.startswith('coconut_65374') and 'aug' in video_name:
            targets.append((video_name, label))
        elif not complete_pkl.exists():
            targets.append((video_name, label))
    if not targets:
        logging.info("All entries already have landmarks_complete.pkl")
        return
    target_idx = 0
    for source_video, source_label in sources:
        source_path = landmark_dir / source_video / 'landmarks_complete.pkl'
        try:
            with open(source_path, 'rb') as f:
                landmarks = pickle.load(f)
            if isinstance(landmarks, dict):
                landmarks = np.concatenate([
                    np.array(landmarks.get('face', np.zeros((57, 468, 3)))),
                    np.array(landmarks.get('left_hand', np.zeros((57, 21, 3)))),
                    np.array(landmarks.get('right_hand', np.zeros((57, 21, 3)))),
                    np.array(landmarks.get('pose', np.zeros((57, 33, 3))))
                ], axis=1)
            elif not isinstance(landmarks, np.ndarray):
                logging.error(f"Unexpected landmark format in {source_video}, skipping")
                continue
            if landmarks.shape[1] != 543 or landmarks.shape[2] != 3:
                logging.error(f"Invalid shape for {source_video}: {landmarks.shape}, expected [frames, 543, 3]")
                continue
            if np.all(landmarks == 0) or np.any(np.isnan(landmarks)):
                logging.error(f"Invalid data in {source_video}: contains zeros or NaNs")
                continue
            for i in range(num_augmentations_per_source):
                if target_idx >= len(targets):
                    break
                target_video, target_label = targets[target_idx]
                target_folder = landmark_dir / target_video
                aug_path = target_folder / 'landmarks_complete.pkl'
                if not target_folder.exists():
                    logging.error(f"Target folder {target_folder} does not exist, skipping")
                    target_idx += 1
                    continue
                aug_landmarks = augment_landmarks(landmarks)
                try:
                    with open(aug_path, 'wb') as f:
                        pickle.dump(aug_landmarks, f)
                    logging.info(f"Saved augmented landmarks_complete.pkl to {aug_path}")
                    target_idx += 1
                except Exception as e:
                    logging.error(f"Failed to save {aug_path}: {e}")
                    target_idx += 1
                    continue
        except Exception as e:
            logging.error(f"Failed to load {source_path}: {e}")
            continue
    logging.info(f"Completed augmentation for {target_idx} targets")

# --- PREPROCESSING ---
def preprocess_landmarks(landmarks, target_frames=190, sigma=1.0, threshold=3.0):
    original_frames, keypoints, coords = landmarks.shape
    if original_frames == 0:
        raise ValueError("Zero frames detected")
    if keypoints != 543 or coords != 3:
        raise ValueError(f"Invalid shape {landmarks.shape}, expected [frames, 543, 3]")
    if original_frames >= target_frames:
        landmarks = landmarks[:target_frames]
    else:
        x = np.linspace(0, 1, original_frames)
        x_new = np.linspace(0, 1, target_frames)
        interpolated = np.zeros((target_frames, keypoints, coords))
        for k in range(keypoints):
            for c in range(coords):
                if np.all(np.isnan(landmarks[:, k, c])) or np.all(landmarks[:, k, c] == 0):
                    interpolated[:, k, c] = np.nan
                else:
                    interp_func = interp1d(x, landmarks[:, k, c], kind='linear', fill_value='extrapolate', bounds_error=False)
                    interpolated[:, k, c] = interp_func(x_new)
        landmarks = interpolated
    smoothed = np.zeros_like(landmarks)
    for k in range(keypoints):
        for c in range(coords):
            if not np.all(np.isnan(landmarks[:, k, c])):
                smoothed[:, k, c] = gaussian_filter1d(landmarks[:, k, c], sigma=sigma, mode='nearest')
    z_scores = np.abs((smoothed - np.nanmean(smoothed, axis=0)) / np.nanstd(smoothed, axis=0))
    mask = (z_scores < threshold) | np.isnan(z_scores)
    cleaned = np.where(mask, smoothed, np.nan)
    for k in range(keypoints):
        for c in range(coords):
            mask_nan = np.isnan(cleaned[:, k, c])
            if np.any(mask_nan):
                x = np.arange(target_frames)
                valid_idx = ~mask_nan
                if np.any(valid_idx):
                    interp_func = interp1d(x[valid_idx], cleaned[valid_idx, k, c], kind='linear', fill_value='extrapolate')
                    cleaned[:, k, c] = interp_func(x)
                else:
                    cleaned[:, k, c] = 0
    if cleaned.shape[0] != target_frames or cleaned.shape[1] != 543 or cleaned.shape[2] != 3:
        raise ValueError(f"Output shape mismatch: {cleaned.shape}, expected {(target_frames, 543, 3)}")
    return cleaned

def process_all_landmarks(landmark_dir, dataset_csv):
    landmark_dir = Path(landmark_dir)
    try:
        dataset = pd.read_csv(dataset_csv)
        if not set(['video_name', 'label']).issubset(dataset.columns):
            raise ValueError(f"Expected columns 'video_name' and 'label' in {dataset_csv}, found: {list(dataset.columns)}")
        logging.info(f"Loaded dataset from {dataset_csv} with {len(dataset)} entries")
    except Exception as e:
        logging.error(f"Failed to load {dataset_csv}: {e}")
        return
    processed_count = 0
    invalid_files = []
    for index, row in dataset.iterrows():
        video_name = row['video_name']
        label = row['label'].lower()
        folder_path = landmark_dir / video_name
        complete_pkl = folder_path / 'landmarks_complete.pkl'
        output_pkl = folder_path / 'landmarks_complete_processed.pkl'
        if complete_pkl.exists():
            try:
                with open(complete_pkl, 'rb') as f:
                    landmarks_complete = pickle.load(f)
                if isinstance(landmarks_complete, dict):
                    landmarks_complete = np.concatenate([
                        np.array(landmarks_complete.get('face', np.zeros((57, 468, 3)))),
                        np.array(landmarks_complete.get('left_hand', np.zeros((57, 21, 3)))),
                        np.array(landmarks_complete.get('right_hand', np.zeros((57, 21, 3)))),
                        np.array(landmarks_complete.get('pose', np.zeros((57, 33, 3))))
                    ], axis=1)
                elif not isinstance(landmarks_complete, np.ndarray):
                    raise ValueError(f"Unexpected format in {complete_pkl}")
                processed_landmarks = preprocess_landmarks(landmarks_complete, target_frames=190)
                os.makedirs(folder_path, exist_ok=True)
                with open(output_pkl, 'wb') as f:
                    pickle.dump(processed_landmarks, f)
                processed_count += 1
                logging.info(f"Processed {video_name}: Saved to {output_pkl}, shape {processed_landmarks.shape}")
            except Exception as e:
                logging.error(f"Failed to process {complete_pkl}: {e}")
                invalid_files.append(video_name)
        else:
            logging.warning(f"landmarks_complete.pkl not found for {video_name}")
            invalid_files.append(video_name)
    logging.info(f"Summary: Total files processed: {processed_count}, Invalid or missing files: {len(invalid_files)}")
    if invalid_files:
        logging.info(f"List of invalid/missing files: {invalid_files}") 