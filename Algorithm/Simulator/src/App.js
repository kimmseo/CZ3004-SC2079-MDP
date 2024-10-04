import React from "react";
import {useState, useEffect} from "react";
import "./Grid.css";
// import APIQuery from "./APIQuery";

const dir = {
  north: 0,
  east: 2,
  south: 4,
  west: 6,
  none: 8,
};

const objDir = {
  north: 0,
  east: 2,
  south: 4,
  west: 6,
  none: 8,
};

const dirString = {
  0: "up",
  2: "right",
  4: "down",
  6: "left",
  8: "none",
}

// transform the coordinates
const transCoor = (x, y) => {
  // change the coordinates to bottom left
  // return {x: 19 - y, y:x}
  return {x: x, y: 19 - y}
};

// Current grid setting is x-axis is y and y-axis is x. top left is 0,0
const transBotCoor = (x, y) => {
  return {x: 19 - y, y: x}
}

function classNames(...classes){
  return classes.filter(Boolean).join(" ");
}

export default function App(){
  // Robot states
  const [botState, setBotState] = useState({
    x: 1,
    y: 1,
    d: dir.north,
    s: -1,
  });
  const [botX, setBotX] = useState(1);
  const [botY, setBotY] = useState(1);
  const [botDir, setBotDir] = useState(0);

  // obstacles state
  const [obstacles, setObstacles] = useState([]);
  const [objXCoor, setObjXCoor] = useState(0);
  const [objYCoor, setObjYCoor] = useState(0);
  const [objDirCoor, setObjDirCoor] = useState(objDir.north);

  // Other technical states
  const [isRunning, setIsRunning] = useState(false);
  const [shortestPath,  setShortestPath] = useState([]);
  const [commands, setCommands] = useState([]);
  const [page, setPage] = useState(0);

  const createID = () =>{
    const isIDUnique = (id) => !obstacles.some(ob => ob.id === id);

    let newID;
    do {
      newID = Math.floor(Math.random() * 10) + 1;
    } while (!isIDUnique(newID));

    return newID;
  }

  // To mark the robot cell area
  const robotArea = () => {
    const robotAreaCell = [];
    let markerX = 0;
    let markerY = 0;

    if(Number(botState.d) === dir.north){
      markerY++;
      // markerX++;
    }else if (Number(botState.d) === dir.east){
      markerX++;
      // markerY++;
    } else if (Number(botState.d) === dir.south){
      markerY--;
      // markerX--;
    } else if(Number(botState.d) === dir.west){
      markerX--;
      // markerY--;
    }

    for(let i = -1; i < 2; i++){
      for(let j = -1; j < 2; j++){
        const coord = transBotCoor(botState.x + i, botState.y + j);
        if(markerX === i && markerY === j){
          // Set the direction of the bot
          robotAreaCell.push({
            x: coord.x,
            y: coord.y,
            d: botState.d,
            s: botState.s,
          });
        }else{
          robotAreaCell.push({
            x: coord.x,
            y: coord.y,
            d: null,
            s: -1,
          });
        }
      }
    }
    return robotAreaCell;
  }

  // Setting the robot coordinates 
  const createBotXCoor = (event) => {
    if(Number.isInteger(Number(event.target.value))){
      const num = Number(event.target.value);
      if(0 <= num && num < 20){
        setBotX(num);
        return;
      }
    }
    // If the input is not an integer or is not in the range, set as 1
    setBotX(1);
  }

  const createBotYCoor = (event) => {
    if(Number.isInteger(Number(event.target.value))){
      const num = Number(event.target.value);
      if(0 <= num && num < 20){
        setBotY(num);
        return;
      }
    }
    // If the input is not an integer or is not in the range, set as 1
    setBotY(1);
  }

  // Set the robot state to shift the position of the robot
  const createRobot = () =>{
    setBotState({
      x: botX,
      y: botY,
      d: botDir,
      s: -1
    });
    
    // Generate robot cells
    const botCells = robotArea(); // creating the robot cell area

    // Generate robot cells
    const updatedGrid = grid.map((row, rowIndex) => (
      row.map((cell, colIndex) => {
        const foundBotCell = botCells.find(cell => cell.x === rowIndex && cell.y === colIndex);
        const foundObstacle = obstacles.some( obstacle => obstacle.x === rowIndex && obstacle.y === colIndex);
        
        if (foundObstacle) {
          // Leave obstacle cells unchanged
          return cell;
        }

        if (foundBotCell) {
          if (foundBotCell.d !== null) {
            // set the direction of the bot
            return { ...cell, color: '#E74C3C' };
          } else {
            // set the bot area color
            return { ...cell, color: '#2E86C1' };
          }
        }

        return { ...cell, color: '' };;
      })
    ));
    // Set the updated grid
    setGrid(updatedGrid);
  };

  const robotDirInput = (event) => {
    setBotDir(event.target.value);
  };

  const reset = () => {
    // Reset the grid to remove all obstacles
    setGrid(createInitialGrid());
    setBotX(1);
    setBotY(1);
    setBotDir(0);
    setBotState({
      x: 1,
      y: 1,
      d: dir.north,
      s: -1
    });
    setShortestPath([]);
    setCommands([]);
    setPage(0);
    setObstacles([]);
  };


  // Grid Settings
  const cellSizeInPixels = 30; // Adjust cell size as needed
  const objSize = 1; // Size of the object region
  
  
  // grid
  const [grid, setGrid] = useState(createInitialGrid());
  
  function createInitialGrid() {
    const columns = 20;
    const rows = 20;
    return Array.from({ length: rows }, () => Array(columns).fill({ color: '#fff' }));
  }

  // Get the obstacle direction using prompt
  const getDirectionFromUser = () => {
    const direction = window.prompt('Enter the direction (up, down, left, right, none):');
    return direction && ['up', 'down', 'left', 'right', 'none'].includes(direction.toLowerCase())
      ? direction.toLowerCase()
      : null;
  };
  
  // Handle object placement on grid
  const handleCellClick = (row, col) => {  
    const direction = getDirectionFromUser();

    // If invalid input return
    if(!row && !col) return;

    // New array of obstacles
    const obArray = [...obstacles];
    const transformXY = transCoor(col, row);

    if (direction) {
      const newGrid = [...grid];

      switch (direction) {
        case 'up':
          newGrid[row][col] = { ...newGrid[row][col], topBorder:true};
          newGrid[row][col] = { ...newGrid[row][col], color: true };
          obArray.push ({
            x: transformXY.x,
            y: transformXY.y,
            d: objDir.north,
            id: createID(),
          });
      
          break;
        case 'down':
          newGrid[row][col] = { ...newGrid[row][col], bottomBorder:true};
          newGrid[row][col] = { ...newGrid[row][col], color: true };
          obArray.push ({
            x: transformXY.x,
            y: transformXY.y,
            d: objDir.south,
            id: createID(),
          });
          break;
        case 'left':
          newGrid[row][col] = { ...newGrid[row][col], leftBorder:true};
          newGrid[row][col] = { ...newGrid[row][col], color: true };
          obArray.push ({
            x: transformXY.x,
            y: transformXY.y,
            d: objDir.west,
            id: createID(),
          });
          break;
        case 'right':
          newGrid[row][col] = { ...newGrid[row][col], rightBorder:true};
          newGrid[row][col] = { ...newGrid[row][col], color: true };
          obArray.push ({
            x: transformXY.x,
            y: transformXY.y,
            d: objDir.east,
            id: createID(),
          });
          break;
        case 'none':
          newGrid[row][col] = { ...newGrid[row][col], noBorder:true};
          newGrid[row][col] = { ...newGrid[row][col], color: true };
          obArray.push ({
            x: transformXY.x,
            y: transformXY.y,
            d: objDir.none,
            id: createID(),
          });
          break;
        default:
          break;
      }
      
      // set to obstacles array
      setObstacles(obArray);
      console.log(obArray);  // To ensure the array object is added
      // Update state
      setGrid(newGrid);
    }
  };

  // Handle the run button
  const handleRunClick = async () => {
    var myHeaders = new Headers()
    myHeaders.append("Content-Type", "application/json");

  var raw = JSON.stringify({
    "obstacles": [...obstacles],
    "retrying": false,
    "size_x": 20,
    "size_y": 20,
    "robot_x": botX,
    "robot_y": botY,
    "robot_direction": botDir
  });

  var requestOptions = {
    method: 'POST',
    headers: myHeaders,
    body: raw,
    redirect: 'follow'
  };

  fetch("http://127.0.0.1:5000/navigate", requestOptions)
    .then(response => response.text())
    .then(result => {
      const json = JSON.parse(result)

      setIsRunning(true);
      if(json){
        // set shortest path
        setShortestPath(json.data.path);
        const commands = [];
        for(let c of json.data.commands){
          // Skip as bot is taking a screenshot of obstacle
          if(c.startsWith("SNAP")){
            continue;
          }
          commands.push(c);
        }
        setCommands(commands);
      }
      setIsRunning(false);

      console.log(json);
    })
    .catch(error => console.log('error', error));
  }

  // Remove all obstacles
  const removeObstacles = () => {
    if (shortestPath.length > 0 || isRunning) return;
    const obArray	= [];
    // set the obstacles array to null
    setObstacles(obArray);
    // Reset the grid to remove all obstacles
    setGrid(createInitialGrid());
    
  };

  // move the robot position
  const moveRobot = () =>{
    // Generate robot cells
    const botCells = robotArea(); // creating the robot cell area

    // Generate robot cells
    const updatedGrid = grid.map((row, rowIndex) => (
      row.map((cell, colIndex) => {
        const foundBotCell = botCells.find(cell => cell.x === rowIndex && cell.y === colIndex);
        const foundObstacle = obstacles.some( obstacle => obstacle.x === rowIndex && obstacle.y === colIndex);
        
        if (foundObstacle) {
          // Leave obstacle cells unchanged
          return cell;
        }

        if (foundBotCell) {
          if (foundBotCell.d !== null) {
            // set the direction of the bot
            return { ...cell, color: '#E74C3C' };
          } else {
            // set the bot area color
            return { ...cell, color: '#2E86C1' };
          }
        }

        return { ...cell, color: '' };;
      })
    ));
    // Set the updated grid
    setGrid(updatedGrid);
  };

  const [triggerBack, setTriggerBack] = useState(false);
  useEffect(() => {
    if(page >= shortestPath.length) return; 
    console.log("PAGE NUMBER: ", page);

    /* Logic:
    Current page starts from 0
    shortestpath is setting the next path due to rendering*/
    if(triggerBack === false){
      console.log("IF statement: ", shortestPath[page +1]);
      setBotState(shortestPath[page + 1]);
      moveRobot();
    }
  }, [page, shortestPath]);

  return (
    <div className="simulator-container">
      <h2 className="header"> Algorithm Simulator</h2>
      <div className="grid-container">
    
        <div className="grid">
            {grid.map((row, rowIndex) => (
              <div key={rowIndex} className="row">
                <h3>{rowIndex < 10? 19 - rowIndex : (19 - rowIndex).toString().padStart(2, '0')}</h3>
                {row.map((cell, colIndex) => (
                  <div
                    key={colIndex}
                    className={`cell ${cell && cell.clicked ? 'active' : ''} ${
                      cell && cell.rightBorder ? 'right-border' : ''
                    } ${cell && cell.leftBorder ? 'left-border' : ''} ${
                      cell && cell.bottomBorder ? 'bottom-border' : ''
                    } ${cell && cell.topBorder ? 'top-border' : ''} ${
                      cell && cell.noBorder ? 'no-Border' : ''} ${
                      cell && cell.robotColorDir ? 'robotColorDir' : ''} ${
                      cell && cell.robotColor ? 'robotColor' : ''}`}
                    style={{
                      width: cellSizeInPixels,
                      height: cellSizeInPixels,
                      backgroundColor: cell.color,
                    }}
                    onClick={() => handleCellClick(rowIndex, colIndex)}
                  >
                    {/* {rowIndex === 19? colIndex: null} */}
                  
                  </div>
                ))}
              </div>
            ))}
            {/*Additional row for the axis */}
            <div className="row">
              <h3>XY</h3>
              {Array.from({ length: grid[0].length }, (_, colIndex) => (
                <div key={colIndex} className="cell">
                  {colIndex}
                </div>
              ))}
            </div>

        </div>
        
        <div className="controller-container">
          <h3 className="subHeader-Con">Robot</h3>
          {/* Path Paging */}
          {shortestPath.length > 0 && (
          <div className="flex flex-row items-center text-center bg-sky-200 p-4 my-8">
            {/* <button className="btn btn-circle pt-2 pl-1" 
            disabled={page === 0}
              onClick={() => {
                setPage(page - 1);
                setTriggerBack(true);
              }}
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M11.354 1.646a.5.5 0 0 1 0 .708L5.707 8l5.647 5.646a.5.5 0 0 1-.708.708l-6-6a.5.5 0 0 1 0-.708l6-6a.5.5 0 0 1 .708 0z"
                />
              </svg>
            </button> */}
            
            <span className="mx-5 text-black">
              Step: {page + 1} / {shortestPath.length}
            </span>
            <span className="mx-5 text-black">{commands[page]}</span>
            <button
              className="btn btn-circle pt-2 pl-2"
              disabled={page === shortestPath.length - 1}
              onClick={() => {
                setPage(page + 1);
                setTriggerBack(false);
              }}
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M4.646 1.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1 0 .708l-6 6a.5.5 0 0 1-.708-.708L10.293 8 4.646 2.354a.5.5 0 0 1 0-.708z"
                />
              </svg>
          </button>
        </div>
      )}

          <div>
            <table className="commandTable">
              <th>
                <td colspan="2">Commands</td>
              </th>
            {commands.map((item, index) => (
              index % 2 === 0 ? (
                <tr key={index}>
                  <td>Step {index} : {item}</td>
                  {/* Render next item if exists */}
                  {commands[index + 1] && <td>Step {index + 1} : {commands[index+1]}</td>}
                </tr>
              ) : null
            ))}
            </table>
          </div>
          <button className="runBtn" onClick={handleRunClick}>Run</button>
          <button className="resetBtn" onClick={reset}>Reset Grid</button>
          <br/>
          {/* <div className="flex flex-col items-center text-center bg-sky-200 rounded-l"> */}
          {/* <div className="card-body items-center text-center p-4"> */}
            <div className="form-control">
            <h3 className="subHeader-Robot">Robot Area</h3>
            <table>
              <tr>
                <td>
                  <span className="bg-primary p-2">X: </span>
              <input 
                onChange={createBotXCoor}
                type="number"
                placeholder="1"
                min="1"
                max = "18"
                className="input input-bordered  text-blue-900 w-20"
              />
                </td>
                <td>
                  <span className="bg-primary p-2">Y: </span>
              <input
                onChange={createBotYCoor}
                type="number"
                placeholder="1"
                min="1"
                max="18"
                className="input input-bordered text-blue-900 w-20"
              />
                </td>
              </tr>
              <tr>
                <td colSpan={2}>
                  <span>Direction: </span>
                  <select onChange={robotDirInput} value={botDir}
                  className="select text-blue-900 pr-10">
                    <option value={objDir.north}>North</option>
                    <option value={objDir.south}>South</option>
                    <option value={objDir.east}>East</option>
                    <option value={objDir.west}>West</option>
                  </select>
                </td>
              </tr>
            </table>
            {/* <label className="input-group input-group-horizontal"> */}   
              <button className="setBtn" onClick={createRobot}>Set</button>
            {/* </label> */}
            </div>
          {/* </div> */}
          {/* </div> */}
          <br/>

          <h3 className="subHeader-Obstacle">Obstacles Created</h3>
          {obstacles.map((ob) => {
            return (
              <div key={ob}>
                <table>
                  <tr></tr>
                </table>
                <div flex flex-col>
                  <div>X: {ob.x}</div>
                  <div>Y: {ob.y}</div>
                  <div>D: {dirString[ob.d]}</div>
                </div>
                {/* <div>
                  <svg xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  className="inline-block w-4 h-4 stroke-current">
                    <path strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M6 18L18 6M6 6l12 12"></path>
                  </svg>
                </div>   */}
              </div>

            )
          })}
        </div>
      </div>

      {/* <table className="border-collapse border-none border-black">
        <tbody>{createGrid()}</tbody>
      </table> */}
      
    </div>
      

  )
}
