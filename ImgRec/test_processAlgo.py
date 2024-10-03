def map_commands_to_paths(data):
    transformed_commands = data["commands"]
    paths = data["path"]
    mapped_commands = []

    # Initialize variables
    non_snap_path_index = 0  # Tracks which path we're on

    segment_start = True  # Flag to indicate if we are at the start of a new segment

    for command in transformed_commands:
        if command in ["FW003", "FW002", "BW002"]:
            # At the start of a segment that requires a path
            if segment_start and non_snap_path_index < len(paths):
                mapped_commands.append((command, [paths[non_snap_path_index]]))
                non_snap_path_index += 1
            else:
                mapped_commands.append((command, None))
            segment_start = False  # Not at the start anymore
        elif command in ["FL090", "FR090", "BL090", "BR090"]:
            # These commands are continuation of a segment, no path assigned
            mapped_commands.append((command, None))
            segment_start = False  # Still not the start of a new segment
        elif command.startswith("SNAP") or command == "FIN":
            # SNAP and FIN are treated as their own segments but don't have paths
            mapped_commands.append((command, None))
            segment_start = True  # Next command could be the start of a new segment
        else:
            # For any command not explicitly handled above, assign the next path if available
            if non_snap_path_index < len(paths):
                mapped_commands.append((command, [paths[non_snap_path_index]]))
                non_snap_path_index += 1
            else:
                mapped_commands.append((command, []))
            segment_start = True  # Next command could be the start of a new segment

    return mapped_commands

if __name__ == "__main__":
    # Provided input data

    data =  {
        "commands": [
            "FW090",
            "FW003",
            "BR090",
            "BW002",
            "BW020",
            "FW003",
            "BR090",
            "BW002",
            "SNAP6_C",
            "BW040",
            "FW003",
            "BL090",
            "BW002",
            "FW050",
            "SNAP1_C",
            "BW090",
            "FW003",
            "BL090",
            "BW002",
            "FW010",
            "SNAP4_C",
            "BW020",
            "FW003",
            "BL090",
            "BW002",
            "SNAP5_C",
            "BW070",
            "FW003",
            "BR090",
            "BW002",
            "SNAP2_C",
            "BW040",
            "FW003",
            "BL090",
            "BW002",
            "FW090",
            "FW010",
            "FW003",
            "FL090",
            "FW090",
            "FW030",
            "FW003",
            "BR090",
            "BW002",
            "FW020",
            "SNAP3_C",
            "FIN"
        ],
        "distance": 184.0,
        "path": [
            {
                "d": 0,
                "s": -1,
                "x": 1,
                "y": 1
            },
            {
                "d": 0,
                "s": -1,
                "x": 1,
                "y": 10
            },
            {
                "d": 6,
                "s": -1,
                "x": 3,
                "y": 7
            },
            {
                "d": 6,
                "s": -1,
                "x": 5,
                "y": 7
            },
            {
                "d": 4,
                "s": 6,
                "x": 8,
                "y": 9
            },
            {
                "d": 4,
                "s": -1,
                "x": 8,
                "y": 13
            },
            {
                "d": 6,
                "s": -1,
                "x": 10,
                "y": 16
            },
            {
                "d": 6,
                "s": 1,
                "x": 5,
                "y": 16
            },
            {
                "d": 6,
                "s": -1,
                "x": 14,
                "y": 16
            },
            {
                "d": 0,
                "s": -1,
                "x": 17,
                "y": 14
            },
            {
                "d": 0,
                "s": 4,
                "x": 17,
                "y": 15
            },
            {
                "d": 0,
                "s": -1,
                "x": 17,
                "y": 13
            },
            {
                "d": 2,
                "s": 5,
                "x": 15,
                "y": 10
            },
            {
                "d": 2,
                "s": -1,
                "x": 8,
                "y": 10
            },
            {
                "d": 0,
                "s": 2,
                "x": 5,
                "y": 8
            },
            {
                "d": 0,
                "s": -1,
                "x": 5,
                "y": 4
            },
            {
                "d": 2,
                "s": -1,
                "x": 3,
                "y": 1
            },
            {
                "d": 2,
                "s": -1,
                "x": 12,
                "y": 1
            },
            {
                "d": 2,
                "s": 6,
                "x": 13,
                "y": 1
            },
            {
                "d": 0,
                "s": -1,
                "x": 15,
                "y": 4
            },
            {
                "d": 0,
                "s": -1,
                "x": 15,
                "y": 13
            },
            {
                "d": 0,
                "s": -1,
                "x": 15,
                "y": 16
            },
            {
                "d": 6,
                "s": -1,
                "x": 17,
                "y": 13
            },
            {
                "d": 6,
                "s": 3,
                "x": 15,
                "y": 13
            }
        ]
    }
    # Correct function call
    command_path_mapping = map_commands_to_paths(data)

    # Output the mapping for review
    for mapping in command_path_mapping:
        print(mapping)