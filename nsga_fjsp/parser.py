from __future__ import annotations

from pathlib import Path
import re


DATASET_ROOT = Path(__file__).resolve().parent.parent / "datasets" / "FJSP"


def read_fjsp_instance(dataset_name, instance_name):
    txt_path = DATASET_ROOT / dataset_name / f"{instance_name}.txt"
    fjs_path = DATASET_ROOT / dataset_name / f"{instance_name}.fjs"

    if txt_path.exists():
        return _read_txt_instance(txt_path)
    if fjs_path.exists():
        return _read_fjs_instance(fjs_path)

    raise FileNotFoundError(f"未找到数据文件：{txt_path} 或 {fjs_path}")


def _read_txt_instance(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        rows = file.read().splitlines()

    work = []
    machine_time = []
    job_index = 0

    for row in rows[1:]:
        if not row:
            continue

        values = [int(value) for value in re.findall(r"[0-9]+", row)]
        work.extend([job_index + 1] * values[0])
        job_index += 1

        remaining = values[1:]
        while remaining:
            candidate_count = remaining[0]
            operation_machine_time = []
            for index in range(candidate_count):
                operation_machine_time += remaining[2 * index + 1 : 2 * index + 3]
            machine_time.append(operation_machine_time)
            remaining = remaining[2 * candidate_count + 1 :]

    return work, machine_time


def _read_fjs_instance(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = [line.strip() for line in file.readlines() if line.strip()]

    header_nums = re.findall(r"[0-9]+(?:\.[0-9]+)?", lines[0])
    if len(header_nums) < 2:
        raise ValueError(f"FJS头部格式不正确: {lines[0]}")

    job_count = int(float(header_nums[0]))
    nums = [int(x) for x in re.findall(r"[0-9]+", "\n".join(lines[1:]))]
    ptr = 0

    work = []
    machine_time = []
    for job_idx in range(job_count):
        if ptr >= len(nums):
            raise ValueError("FJS解析越界：缺少工序数量")
        operation_count = nums[ptr]
        ptr += 1
        work.extend([job_idx + 1] * operation_count)

        for _ in range(operation_count):
            if ptr >= len(nums):
                raise ValueError("FJS解析越界：缺少候选机器数量")
            candidate_count = nums[ptr]
            ptr += 1

            operation_machine_time = []
            for _ in range(candidate_count):
                if ptr + 1 >= len(nums):
                    raise ValueError("FJS解析越界：缺少(机器,时间)对")
                machine_id = nums[ptr]
                processing_time = nums[ptr + 1]
                ptr += 2
                operation_machine_time += [machine_id, processing_time]
            machine_time.append(operation_machine_time)

    return work, machine_time
