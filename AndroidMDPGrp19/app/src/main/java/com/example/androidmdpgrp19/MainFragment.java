package com.example.androidmdpgrp19;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Bundle;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;

import android.util.Log;
import android.view.LayoutInflater;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONArray;
import org.json.JSONObject;

import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.List;
import java.util.Timer;
import java.util.TimerTask;

public class MainFragment extends Fragment {

    // the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
    private static final String ARG_PARAM1 = "param1";
    private static final String ARG_PARAM2 = "param2";
    public static String TAG = "MainFragment";

    private View rootView;

    private static GridMap gridMap;

    //

    private boolean initializedIntentListeners = false;
    private TextView txtRoboStatus;
    //For Arena
    boolean placingRobot, settingObstacle, settingDir;

    //For Obstacle listview
    private ObstaclesListViewAdapter obstaclesListViewAdapter;
    private List<ObstacleListItem> obstacleListItemList;

    //Auxiliary
    private long timeStarted;
    private long timeEnded;
    private long timeTakenInNanoSeconds;

    //Android widgets for UI
    //ROBOT RELATED
    Button btnSendArenaInfo;
    Button btnSendStartImageRec;
    Button btnSendStartFastestCar;

    //ARENA RELATED
    Button btnStop;
    Button btnResetArena;
    Button btnSetObstacle;
    Button btnSetFacing;
    Button btnPlaceRobot;

    //Adding obstacles using buttons
    Button btnAddObsManual;
    EditText addObs_x;
    EditText addObs_y;

    //Bot Status
    TextView txtTimeTaken;


    // DEBUGGING PURPOSES
    int[] robotPos;
    int xcoord, ycoord;
    GridMap.Direction robotDir;


    public MainFragment() {
        // Required empty public constructor
    }

    public static MainFragment newInstance(String param1, String param2) {
        MainFragment fragment = new MainFragment();
        Bundle args = new Bundle();
        args.putString(ARG_PARAM1, param1);
        args.putString(ARG_PARAM2, param2);
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        obstacleListItemList = new ArrayList<>();

        if(!initializedIntentListeners){
            LocalBroadcastManager.getInstance(getContext()).registerReceiver(roboStatusUpdateReceiver, new IntentFilter("updateRobocarStatus"));
            LocalBroadcastManager.getInstance(getContext()).registerReceiver(roboStateReceiver, new IntentFilter("updateRobocarState"));
            LocalBroadcastManager.getInstance(getContext()).registerReceiver(roboModeReceiver, new IntentFilter("updateRobocarMode"));
            LocalBroadcastManager.getInstance(getContext()).registerReceiver(updateObstacleListReceiver, new IntentFilter("newObstacleList"));
            LocalBroadcastManager.getInstance(getContext()).registerReceiver(imageRecResultReceiver, new IntentFilter("imageResult"));
            LocalBroadcastManager.getInstance(getContext()).registerReceiver(robotLocationUpdateReceiver, new IntentFilter("updateRobocarLocation"));

            initializedIntentListeners = true;
        }

    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        rootView = inflater.inflate(R.layout.main_fragment_layout, container, false);

        if(gridMap == null){
            gridMap = new GridMap(getContext());
            gridMap = rootView.findViewById(R.id.mapView);
        }

        //
        //For obstacle list view
        ListView obstacleListView = (ListView)  rootView.findViewById(R.id.home_obstacles_listview);
        obstaclesListViewAdapter = new ObstaclesListViewAdapter(getContext(), R.layout.obstacle_list_item, obstacleListItemList);
        obstacleListView.setAdapter(obstaclesListViewAdapter);

        //Initialize Flags
        placingRobot = false;

        // For updating of robot status
        this.txtRoboStatus = (TextView) rootView.findViewById(R.id.robotStatusText);

        //CONTROL BUTTON DECLARATIONS
        ImageButton controlBtnUp = rootView.findViewById(R.id.upArrowBtn);
        ImageButton controlBtnDown = rootView.findViewById(R.id.downArrowBtn);
        ImageButton controlBtnLeft = rootView.findViewById(R.id.leftArrowBtn);
        ImageButton controlBtnRight = rootView.findViewById(R.id.rightArrowBtn);

        // DEBUGGING PURPOSES


        controlBtnUp.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View v, MotionEvent event) {
                if(event.getAction() == MotionEvent.ACTION_DOWN) {
                    sendDirectionCmdIntent("FW50");
                    robotPos = GridMap.getCurrentCoord();
                    // if the robot is not set
                    if (robotPos == null || (robotPos[0] == -1 && robotPos[1] == -1)) {
                        Toast.makeText(getContext(), "Robot not set", Toast.LENGTH_SHORT).show();
                        return true;
                    }

                    // DEBUGGING
                    xcoord = robotPos[0];
                    ycoord = robotPos[1];
                    Log.v(TAG, "Position of robot:" + xcoord + ", " + ycoord);
                    ycoord += 1;
                    gridMap.updateCurCoord(xcoord, ycoord, gridMap.getRobotDirection());
                    // gridMap.updateRobotStatusTextView(xcoord, ycoord, gridMap.getRobotDirection());

                    Log.d("Movement", "Move Up");
                }
                return true;
            }
        });

        //CONTROL BUTTON: Reverse
        controlBtnDown.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View v, MotionEvent event) {
                if(event.getAction() == MotionEvent.ACTION_DOWN) {
                    sendDirectionCmdIntent("BW10");
                    robotPos = GridMap.getCurrentCoord();
                    if (robotPos == null || (robotPos[0] == -1 && robotPos[1] == -1)) {
                        Toast.makeText(getContext(), "Robot not set", Toast.LENGTH_SHORT).show();
                        return true;
                    }

                    // DEBUGGING
                    xcoord = robotPos[0];
                    ycoord = robotPos[1];
                    ycoord -= 1;
                    gridMap.updateCurCoord(xcoord, ycoord, gridMap.getRobotDirection());

                    Log.d("Movement", "Move Down");

                }
                return true;
            }
        });

        //CONTROL BUTTON: Left
        controlBtnLeft.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View v, MotionEvent event) {
                if(event.getAction() == MotionEvent.ACTION_DOWN) {
                    sendDirectionCmdIntent("FL00");

                    robotPos = GridMap.getCurrentCoord();
                    if (robotPos == null || (robotPos[0] == -1 && robotPos[1] == -1)) {
                        Toast.makeText(getContext(), "Robot not set", Toast.LENGTH_SHORT).show();
                        return true;
                    }

                    // DEBUGGING
                    xcoord = robotPos[0];
                    ycoord = robotPos[1];
                    xcoord -= 3;
                    ycoord += 2;
                    robotDir = GridMap.Direction.LEFT;
                    gridMap.updateCurCoord(xcoord, ycoord, robotDir);

                    Log.d("Movement", "Move Left");

                }
                return true;
            }
        });

        //CONTROL BUTTON: Right
        controlBtnRight.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View v, MotionEvent event) {
                if(event.getAction() == MotionEvent.ACTION_DOWN) {
                    sendDirectionCmdIntent("FR00");
                    robotPos = GridMap.getCurrentCoord();
                    if (robotPos == null || (robotPos[0] == -1 && robotPos[1] == -1)) {
                        Toast.makeText(getContext(), "Robot not set", Toast.LENGTH_SHORT).show();
                        return true;
                    }

                    // DEBUGGING
                    xcoord = robotPos[0];
                    ycoord = robotPos[1];
                    xcoord += 3;
                    ycoord += 2;
                    robotDir = GridMap.Direction.RIGHT;
                    Log.d(TAG, "Update robot direction in Home: " + robotDir.toString());
                    gridMap.updateCurCoord(xcoord, ycoord, robotDir);
                    // gridMap.updateRobotStatusTextView(xcoord, ycoord, gridMap.getRobotDirection());

                    Log.d("Movement", "Move Right");

                }
                return true;
            }
        });

        //TIME TAKEN TEXTVIEW
        txtTimeTaken = rootView.findViewById(R.id.txt_timeTaken);

        //ROBOT RELATED
        btnStop = rootView.findViewById(R.id.stop_btn);
        btnSendArenaInfo = rootView.findViewById(R.id.btnSendInfo);
        btnSendStartImageRec = rootView.findViewById(R.id.btnImageRec);
        btnSendStartFastestCar = rootView.findViewById(R.id.btnFastestCar);

        //ARENA RELATED
        btnResetArena = rootView.findViewById(R.id.btnResetArena);
        btnSetObstacle = rootView.findViewById(R.id.btnSetObstacle);
        btnSetFacing = rootView.findViewById(R.id.btnDirectionFacing);
        btnPlaceRobot = rootView.findViewById(R.id.btnPlaceRobot);

        //Adding obstacles using buttons
        btnAddObsManual = rootView.findViewById(R.id.add_obs_btn);
        addObs_x = rootView.findViewById(R.id.add_obs_x_value);
        addObs_y = rootView.findViewById(R.id.add_obs_y_value);

        // OnClickListeners for sending arena info to RPI
        btnStop.setOnClickListener(v->{
            sendStopCmdIntent("STOP");
        });

        btnSendArenaInfo.setOnClickListener(v->{
            gridMap.sendUpdatedObstacleInformation();
        });

        btnSendStartFastestCar.setOnClickListener(v->{
            txtTimeTaken.setText("Time Taken: Waiting for FINISHED");
            timeStarted = System.nanoTime();
            sendControlCmdIntent("start");
        });

        btnSendStartImageRec.setOnClickListener(v->{
            gridMap.removeAllTargetIDs();
            txtTimeTaken.setText("Time Taken: Waiting for FINISHED");
            sendControlCmdIntent("start");
            timeStarted = System.nanoTime();
            new Timer().schedule(new TimerTask() {
                @Override
                public void run() {
                    sendControlCmdIntent("stop");
                }
            }, 360000);
        });

        btnResetArena.setOnClickListener(v->{
            try{
                gridMap.resetMap();
            }catch (Exception e){
                Log.e(TAG, "onCreateView: An error occurred while resetting map");
                e.printStackTrace();
            }
        });

        // OnClickListeners for the arena related buttons
        btnPlaceRobot.setOnClickListener(v -> {
            try{
                //New status
                placingRobot = !placingRobot;
                if(placingRobot) {
                    gridMap.setStartCoordStatus(placingRobot);
                    btnPlaceRobot.setText("Stop Set Robot");
                    btnPlaceRobot.setEnabled(true);

                    btnSetObstacle.setEnabled(false);
                    btnSetFacing.setEnabled(false);
                    btnResetArena.setEnabled(false);
                    btnSendStartFastestCar.setEnabled(false);
                    btnSendStartImageRec.setEnabled(false);

                    placingRobot = !placingRobot;
                }
            }catch (Exception e){
                Log.e(TAG, "onCreateView: An error occurred while placing robot");
                e.printStackTrace();
            }
        });

        btnSetObstacle.setOnClickListener(v->{
            try{
                settingObstacle = !settingObstacle;
                if(settingObstacle){
                    gridMap.setSetObstacleStatus(settingObstacle);
                    btnSetObstacle.setText("Stop Set Obstacle");

                    btnPlaceRobot.setEnabled(false);
                    btnSetFacing.setEnabled(false);
                    btnResetArena.setEnabled(false);
                    btnSendStartFastestCar.setEnabled(false);
                    btnSendStartImageRec.setEnabled(false);

                }else{
                    gridMap.setSetObstacleStatus(settingObstacle);
                    btnSetObstacle.setText("Set Obstacle");
                    btnSetObstacle.setEnabled(true);

                    btnPlaceRobot.setEnabled(true);
                    btnSetFacing.setEnabled(true);
                    btnResetArena.setEnabled(true);
                    btnSendStartFastestCar.setEnabled(true);
                    btnSendStartImageRec.setEnabled(true);
                }
            }catch (Exception e){
                Log.e(TAG, "onCreateView: An error occurred while setting obstacle");
                e.printStackTrace();
            }
        });

        btnSetFacing.setOnClickListener(v -> {
            try{
                settingDir = !settingDir;
                if(settingDir){
                    gridMap.setSetObstacleDirection(settingDir);
                    btnSetFacing.setText("Stop Set Facing");

                    btnSetObstacle.setEnabled(false);
                    btnPlaceRobot.setEnabled(false);
                    btnResetArena.setEnabled(false);
                    btnSendStartFastestCar.setEnabled(false);
                    btnSendStartImageRec.setEnabled(false);
                }else{
                    gridMap.setSetObstacleDirection(settingDir);
                    btnSetFacing.setText("Set Facing");
                    btnSetFacing.setEnabled(true);

                    btnSetObstacle.setEnabled(true);
                    btnPlaceRobot.setEnabled(true);
                    btnResetArena.setEnabled(true);
                    btnSendStartFastestCar.setEnabled(true);
                    btnSendStartImageRec.setEnabled(true);
                }
            }catch (Exception e){
                Log.e(TAG, "onCreateView: An error occurred while setting obstacle direction");
                e.printStackTrace();
            }
        });

        btnAddObsManual.setOnClickListener(v -> {
            try{
                String x_value = addObs_x.getText().toString();
                String y_value = addObs_y.getText().toString();
                try
                {
                    int x_value_int = Integer.parseInt(x_value);
                    int y_value_int = Integer.parseInt(y_value);

                    if( x_value_int < 20 && x_value_int >=0 && y_value_int < 20 && y_value_int >=0){
                        gridMap.setObstacleCoord(x_value_int, y_value_int);
                        displayShortToast("Added obstacle");
                        addObs_x.setText("");
                        addObs_y.setText("");
                    }else{
                        displayShortToast("Invalid Coordinates");
                    }
                }catch (Exception e){
                    displayShortToast("Incorrect values!");
                }
            }catch (Exception e){
                Log.e(TAG, "onCreateView: An error occurred while adding obstacle manually");
                e.printStackTrace();
            }
        });

        return rootView;
    }

    private BroadcastReceiver roboStatusUpdateReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            try{
                String msgInfo = intent.getStringExtra("msg");
                txtRoboStatus.setText(msgInfo);
            }catch (Exception e){
                txtRoboStatus.setText("UNKNOWN");
                displayShortToast("Error updating robocar status");
                Log.e(TAG, "onReceive: An error occurred while updating the robocar status");
                e.printStackTrace();
            }
        }
    };

    private BroadcastReceiver roboStateReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            try{
                String state = intent.getStringExtra("msg");
                switch(state.toUpperCase()){
                    case "FINISHED":
                        timeEnded = System.nanoTime();
                        timeTakenInNanoSeconds = timeEnded - timeStarted;

                        double timeTakenInSeconds = (double) timeTakenInNanoSeconds/1000000000;
                        int timeTakenMin = (int) timeTakenInSeconds/60;
                        double timeTakenSec = (double) timeTakenInSeconds%60;
                        DecimalFormat df = new DecimalFormat("0.00");

                        txtTimeTaken.setText("Run completed in: "+Integer.toString(timeTakenMin)+"min "+df.format(timeTakenSec)+"secs");

                        btnSetObstacle.setEnabled(true);
                        btnPlaceRobot.setEnabled(true);
                        btnResetArena.setEnabled(true);
                        btnSetFacing.setEnabled(true);
                        btnSendArenaInfo.setEnabled(true);
                        btnAddObsManual.setEnabled(true);
                        break;
                    case "RUNNING":
                        btnSetObstacle.setEnabled(false);
                        btnPlaceRobot.setEnabled(false);
                        btnResetArena.setEnabled(false);
                        btnSetFacing.setEnabled(false);
                        btnSendArenaInfo.setEnabled(false);
                        btnAddObsManual.setEnabled(false);
                        break;
                }
            }catch (Exception ex){
                Log.e(TAG, "onReceive: Error receiving robot completion status");
            }
        }
    };

    private BroadcastReceiver roboModeReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            try{
                String msgInfo = intent.getStringExtra("msg");
                sendModeCmdIntent(msgInfo);
            }catch (Exception e) {
                displayShortToast("Error updating robocar control mode");
                Log.e(TAG, "onReceive: An error occurred while updating the robocar control mode");
                e.printStackTrace();
            }
        }
    };

    private BroadcastReceiver updateObstacleListReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            obstacleListItemList.clear();
            try{
                JSONArray msgInfo = new JSONArray(intent.getStringExtra("msg"));
                for(int i=0; i<msgInfo.length(); i++){
                    JSONObject obj = msgInfo.getJSONObject(i);
                    obstacleListItemList.add(new ObstacleListItem(obj.getInt("no"), obj.getInt("x"),obj.getInt("y"),obj.getString("facing")));
                }
                obstaclesListViewAdapter.updateList(obstacleListItemList);
            }catch (Exception ex){
                Log.e(TAG, "onReceive: An error occurred while updating obstacle list view");
                ex.printStackTrace();
            }
        }
    };

    private BroadcastReceiver robotLocationUpdateReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            try{
                JSONObject msgJSON = new JSONObject(intent.getStringExtra("msg"));
                int xCoord = msgJSON.getInt("x");
                int yCoord = msgJSON.getInt("y");
                int dirInt = msgJSON.getInt("d");
                GridMap.Direction direction = GridMap.Direction.UP;
                Log.d(TAG, msgJSON.toString());
                switch(dirInt){
                    case 0: //NORTH
                        direction = GridMap.Direction.UP;
                        break;
                    case 2: //EAST
                        direction = GridMap.Direction.RIGHT;
                        break;
                    case 4: //SOUTH
                        direction = GridMap.Direction.DOWN;
                        break;
                    case 6: //WEST
                        direction = GridMap.Direction.LEFT;
                        break;
                }

                if(xCoord < 0 || yCoord < 0 || xCoord > 20 || yCoord > 20){
                    displayShortToast("Error: Robot move out of area (x: "+xCoord+", y: "+yCoord+")");
                    Log.e(TAG, "onReceive: Robot is out of the arena area");
                    return;
                }

                gridMap.updateCurCoord(xCoord, yCoord, direction);
            }catch (Exception e){
                displayShortToast("Error updating robot location");
                Log.e(TAG, "onReceive: An error occurred while updating robot location");
                e.printStackTrace();
            }
        }
    };

    private BroadcastReceiver imageRecResultReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            try{
                JSONObject msgJSON = new JSONObject(intent.getStringExtra("msg"));
                int obstacleID = Integer.parseInt(msgJSON.getString("obstacle_id"));
                String targetID = msgJSON.getString("image_id");
                String display = identifiedObstacle(targetID);
                gridMap.updateImageNumberCell(obstacleID, display);
            }catch (Exception e){
                displayShortToast("Error updating image rec result");
                Log.e(TAG, "onReceive: An error occurred while updating the image rec result");
                e.printStackTrace();
            }
        }
    };

    private String identifiedObstacle(String targetID) {
        switch (targetID) {
            case "11":
                return "1";
            case "12":
                return "2";
            case "13":
                return "3";
            case "14":
                return "4";
            case "15":
                return "5";
            case "16":
                return "6";
            case "17":
                return "7";
            case "18":
                return "8";
            case "19":
                return "9";
            case "20":
                return "A";
            case "21":
                return "B";
            case "22":
                return "C";
            case "23":
                return "D";
            case "24":
                return "E";
            case "25":
                return "F";
            case "26":
                return "G";
            case "27":
                return "H";
            case "28":
                return "S";
            case "29":
                return "T";
            case "30":
                return "U";
            case "31":
                return "V";
            case "32":
                return "W";
            case "33":
                return "X";
            case "34":
                return "Y";
            case "35":
                return "Z";
            case "36":
                return "↑";  //up
            case "37":
                return "↓"; //down
            case "38":
                return "→"; //right
            case "39":
                return "←"; //left
            case "40":
                return "stop"; //stop
            default:
                return "na";
        }
    }

    private void displayShortToast(String msg) {
        Toast.makeText(getActivity(), msg, Toast.LENGTH_SHORT).show();
    }

    /*
     * Messages are sent to the RPI in the following format: { "cat": "xxx", "value": "xxx" }
     * The cat (for category) field with the following possible values:
     *   info: general messages
     *   error: error messages, usually in response of an invalid action
     *   location: the current location of the robot (in Path mode)
     *   image-rec: image recognition results
     *   status: status updates of the robot (running or finished)
     *   obstacle: list of obstacles
     *   control: movement-related, like starting the run
     */

    // Sends command about direction of robot
    private void sendDirectionCmdIntent(String direction) {
        try{
            /* UNCOMMENT FOR INTEGRATION WITH RPI */
            JSONObject directionJSONObj = new JSONObject();
            directionJSONObj.put("cat","manual");
            directionJSONObj.put("value", direction);
            broadcastSendBTIntent(directionJSONObj.toString());
        }catch (Exception e){
            Log.e(TAG, "sendDirectionCmdIntent: An error occurred while sending direction command intent");
            e.printStackTrace();
        }
    }

    public void sendModeCmdIntent(String mode){
        try{
            if(!mode.equals("path") && !mode.equals("manual")){
                Log.i(TAG, "sendModeIntent: Invalid mode to send: " + mode);
                return;
            }
            JSONObject modeJSONObj = new JSONObject();
            modeJSONObj.put("cat","mode");
            modeJSONObj.put("value",mode);

            broadcastSendBTIntent(modeJSONObj.toString());
        }catch (Exception e){
            Log.e(TAG, "sendModeIntent: An error occurred while sending mode command intent");
            e.printStackTrace();
        }
    }

    private void sendControlCmdIntent(String control){
        try{
            /* UNCOMMENT FOR INTEGRATION WITH RPI */
            JSONObject ctrlJSONObj = new JSONObject();
            ctrlJSONObj.put("cat","control");
            ctrlJSONObj.put("value",control);
            broadcastSendBTIntent(ctrlJSONObj.toString());

        }catch (Exception e){
            Log.e(TAG, "sendControlCmdIntent: An error occurred while sending control command intent");
            e.printStackTrace();
        }
    }

    private void sendStopCmdIntent(String control){
        try{
            /* UNCOMMENT FOR INTEGRATION WITH RPI */
            JSONObject ctrlJSONObj = new JSONObject();
            ctrlJSONObj.put("cat","manual");
            ctrlJSONObj.put("value", control);
            broadcastSendBTIntent(ctrlJSONObj.toString());

            /* UNCOMMENT FOR TESTING WITH AMDTOOL */
            // broadcastSendBTIntent(control);
        }catch (Exception e){
            Log.e(TAG, "sendStopCmdIntent: An error occurred while sending control command intent");
            e.printStackTrace();
        }
    }

    void broadcastSendBTIntent(String msg){
        Intent sendBTIntent = new Intent("sendBTMessage");
        sendBTIntent.putExtra("msg",msg);
        LocalBroadcastManager.getInstance(getContext()).sendBroadcast(sendBTIntent);
    }

    private class ObstaclesListViewAdapter extends ArrayAdapter<ObstacleListItem> {
        private List<ObstacleListItem> items;

        public ObstaclesListViewAdapter(@NonNull Context context, int resource, @NonNull List<ObstacleListItem> objects) {
            super(context, resource, objects);
            items=objects;
        }

        public void updateList(List<ObstacleListItem> list) {
            this.items = list;
            this.notifyDataSetChanged();
        }

        @NonNull
        @Override
        public View getView(int position, @Nullable View convertView, @NonNull ViewGroup parent) {
            if (convertView == null) {
                convertView = LayoutInflater.from(getContext()).inflate(R.layout.obstacle_list_item, parent, false);
            }
            ObstacleListItem item = items.get(position);
            TextView obsNoTxt = (TextView) convertView.findViewById(R.id.txtObsListItem_obsNo);
            TextView xPosTxt = (TextView) convertView.findViewById(R.id.txtObsListItem_x);
            TextView yPosTxt = (TextView) convertView.findViewById(R.id.txtObsListItem_y);
            TextView facingTxt = (TextView) convertView.findViewById(R.id.txtObsListItem_dir);

            obsNoTxt.setText("#"+item.obsNo);
            xPosTxt.setText(Integer.toString(item.x));
            yPosTxt.setText(Integer.toString(item.y));
            facingTxt.setText(item.facing);

            return convertView;
        }
    }

    private class ObstacleListItem {
        int obsNo;
        int x;
        int y;
        String facing;

        public ObstacleListItem(int obsNo,int x, int y, String facing){
            this.obsNo = obsNo;
            this.x=x;
            this.y=y;
            this.facing=facing;
        }
    }
}