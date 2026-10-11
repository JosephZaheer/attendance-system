import pickle

with open("/workspaces/attendance-system/attendance_system/year_list.dat", "wb") as f:
    years = [2024, 2025, 2026]
    pickle.dump(years, f)

#/workspaces/attendance-system/attendance_system/year_list.dat