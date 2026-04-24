from __future__ import annotations

import numpy as np


class FJSPDecoder:
    def __init__(self, work, machine_time):
        self.work = work
        self.machine_time = machine_time

    def calculate(self, os_code, ms_code):
        job_num = max(os_code)
        machine_num = max(ms_code)
        t_job = np.zeros((1, job_num), dtype=int)
        t_machine = np.zeros((1, machine_num), dtype=int)

        machine_processing_energy = np.zeros(machine_num)
        machine_processing_time = np.zeros(machine_num)

        processing_power = 30.0
        idle_power = 1.0
        count = np.zeros((1, job_num), dtype=int)

        for idx in range(len(os_code)):
            job_idx = os_code[idx] - 1
            op_idx = self.work.index(job_idx + 1) + count[0, job_idx]
            machine_id = ms_code[op_idx]

            start_time = max(t_machine[0, machine_id - 1], t_job[0, job_idx])
            processing_time = self.get_processing_time(op_idx, machine_id)

            machine_processing_energy[machine_id - 1] += processing_time * processing_power
            machine_processing_time[machine_id - 1] += processing_time

            finish_time = start_time + processing_time
            t_machine[0, machine_id - 1] = finish_time
            t_job[0, job_idx] = finish_time
            count[0, job_idx] += 1

        c_max = max(t_job[0])
        machine_idle_energy = np.zeros(machine_num)
        for machine_idx in range(machine_num):
            idle_time = c_max - machine_processing_time[machine_idx]
            machine_idle_energy[machine_idx] = idle_power * idle_time

        total_energy = np.sum(machine_processing_energy) + np.sum(machine_idle_energy)
        return [float(c_max), float(total_energy)]

    def decode_with_details(self, job_code, machine_code):
        job_num = max(job_code)
        machine_num = max(machine_code)

        t_job = np.zeros(job_num, dtype=int)
        t_machine = np.zeros(machine_num, dtype=int)

        machine_processing_energy = np.zeros(machine_num)
        machine_processing_time = np.zeros(machine_num)

        processing_power = 30.0
        idle_power = 1.0
        count = np.zeros(job_num, dtype=int)

        operations = []

        for seq_idx in range(len(job_code)):
            job_idx = job_code[seq_idx] - 1
            op_idx = self.work.index(job_idx + 1) + count[job_idx]
            op_id = int(count[job_idx]) + 1
            machine_id = int(machine_code[op_idx])

            start_time = max(int(t_machine[machine_id - 1]), int(t_job[job_idx]))
            processing_time = self.get_processing_time(op_idx, machine_id)

            machine_processing_energy[machine_id - 1] += processing_time * processing_power
            machine_processing_time[machine_id - 1] += processing_time

            finish_time = start_time + processing_time
            t_machine[machine_id - 1] = finish_time
            t_job[job_idx] = finish_time
            count[job_idx] += 1

            operations.append(
                {
                    "seq_id": seq_idx + 1,
                    "job_id": job_idx + 1,
                    "op_id": op_id,
                    "machine_id": machine_id,
                    "start_time": start_time,
                    "finish_time": finish_time,
                    "process_time": processing_time,
                }
            )

        c_max = int(max(t_job)) if len(t_job) > 0 else 0
        machine_idle_energy = np.zeros(machine_num)
        for machine_idx in range(machine_num):
            idle_time = c_max - machine_processing_time[machine_idx]
            machine_idle_energy[machine_idx] = idle_power * idle_time

        total_energy = np.sum(machine_processing_energy) + np.sum(machine_idle_energy)
        return {
            "objectives": {
                "makespan": float(c_max),
                "energy": float(total_energy),
            },
            "operations": operations,
            "machine_num": machine_num,
        }

    def get_processing_time(self, operation_idx, machine_id):
        if operation_idx < len(self.machine_time):
            machine_time_pairs = self.machine_time[operation_idx]
            for idx in range(0, len(machine_time_pairs), 2):
                if idx + 1 < len(machine_time_pairs) and machine_time_pairs[idx] == machine_id:
                    return machine_time_pairs[idx + 1]

        print(f"Warning: No processing time found for operation {operation_idx} on MS {machine_id}")
        return 1
