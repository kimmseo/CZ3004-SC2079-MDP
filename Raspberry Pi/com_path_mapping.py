def map_commands_to_paths(data):
    commands = data["commands"]
    paths = data["path"]
    mapped_commands = []

    # Iterate over commands to initially assign non-SNAP paths
    non_snap_paths = [path for path in paths if path["s"] == -1]
    non_snap_path_index = 0  # Index to track the non-SNAP path being assigned

    # First pass: Assign non-SNAP paths and placeholders for SNAP paths
    for command in commands:
        if "SNAP" not in command and "FIN" not in command:
            if non_snap_path_index < len(non_snap_paths):
                mapped_commands.append((command, [non_snap_paths[non_snap_path_index]]))
                non_snap_path_index += 1
            else:
                mapped_commands.append((command, []))  # No more non-SNAP paths available
        else:
            mapped_commands.append((command, None))  # SNAP and FIN commands initially get no path

    # Second pass: Assign SNAP paths to preceding commands
    for i, command in enumerate(commands):
        if "SNAP" in command:
            snap_id = int(command.split("_")[0].replace("SNAP", ""))
            snap_path = next((path for path in paths if path["s"] == snap_id), None)
            if snap_path:
                # Find the previous non-SNAP, non-FIN command to append the SNAP path
                for j in range(i - 1, -1, -1):
                    if mapped_commands[j][1] is not None:  # Ensure it's not a SNAP or FIN command
                        mapped_commands[j][1].append(snap_path)
                        break

    return mapped_commands

if __name__ == "__main__":
    # Provided input data
    data = {
        "commands": [
            "FW050", "BR000", "BL000", "SNAP1_C", "FW010", "FR000", "FW030", "BL000",
            "SNAP2_C", "FW010", "BL000", "FW020", "BR000", "FW010", "BL000", "SNAP3_C", "FIN"
        ],
        "path": [
            {"d": 0, "s": -1, "x": 1, "y": 1}, {"d": 0, "s": -1, "x": 1, "y": 6},
            {"d": 6, "s": -1, "x": 2, "y": 3}, {"d": 0, "s": 1, "x": 5, "y": 2},
            {"d": 0, "s": -1, "x": 5, "y": 3}, {"d": 2, "s": -1, "x": 8, "y": 4},
            {"d": 2, "s": -1, "x": 11, "y": 4}, {"d": 4, "s": 2, "x": 8, "y": 5},
            {"d": 4, "s": -1, "x": 8, "y": 4}, {"d": 6, "s": -1, "x": 9, "y": 7},
            {"d": 6, "s": -1, "x": 11, "y": 7}, {"d": 4, "s": -1, "x": 14, "y": 8},
            {"d": 4, "s": -1, "x": 14, "y": 7}, {"d": 6, "s": 3, "x": 15, "y": 10}
        ],
        "distance": 104.0
    }

    # Correct function call
    command_path_mapping = map_commands_to_paths(data)

    # Output the mapping for review
    for mapping in command_path_mapping:
        print(mapping)