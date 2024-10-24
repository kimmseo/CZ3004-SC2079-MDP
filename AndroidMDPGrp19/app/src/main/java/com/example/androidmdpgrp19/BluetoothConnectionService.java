package com.example.androidmdpgrp19;

import android.annotation.SuppressLint;
import android.app.ProgressDialog;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothServerSocket;
import android.bluetooth.BluetoothSocket;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.util.Log;
import android.widget.Toast;

import androidx.localbroadcastmanager.content.LocalBroadcastManager;


import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.Charset;
import java.util.Arrays;
import java.util.List;
import java.util.UUID;

public class BluetoothConnectionService {
    public static final String TAG = "BTConnectionService";
    private static final String appName = "MDP19Android";
    //UUID change
    private static final UUID MY_UUID = UUID.fromString("00001101-0000-1000-8000-00805F9B34FC");
    private final BluetoothAdapter bluetoothAdapter;
    private BluetoothDevice bluetoothDevice;
    private UUID deviceUUID;
    Context context;
    private AcceptThread acceptThread;
    private ConnectThread connectThread;
    private static ConnectedThread connectedThread;

    private ProgressDialog progressDialog;

    public static boolean isConnected = false;

    public BluetoothConnectionService(Context context){
        //context is Bluetooth frag Context
        this.context = context;
        this.bluetoothAdapter = BluetoothAdapter.getDefaultAdapter();
        start();
    }

    /**
     * AcceptThread runs while listening for incoming connections. It behaves
     * like a server-side client. It runs until a connection is accepted
     * (or until cancelled).
     */
    private class AcceptThread extends Thread{
        //Local Server Socket
        private final BluetoothServerSocket serverSocket;
        @SuppressLint("MissingPermission")
        public AcceptThread(){
            BluetoothServerSocket temp = null;

            try{
                temp = bluetoothAdapter.listenUsingInsecureRfcommWithServiceRecord(appName, MY_UUID);
                LogMessage(temp.toString());
                LogMessage("Setting up server using "+ MY_UUID);
            }catch (IOException e){
                Log.e(TAG, "AcceptThread: IO Exception "+e.getMessage());
            }
            serverSocket = temp;
        }

        public void run(){
            LogMessage( "AcceptThread: run");
            BluetoothSocket socket = null;
            try{
                LogMessage( "run: RFCOM server socket start.....");
                // Blocking call, returns on a successful connection or an exception only
                LogMessage(serverSocket.toString());
                socket = serverSocket.accept();
                LogMessage("run: RFCOM server socket accepted connection.");
            }catch (IOException e){
                Log.e(TAG, "AcceptThread: IOException: " + e.getMessage() );
            }

            if(socket != null){
                bluetoothDevice = socket.getRemoteDevice();
                connected(socket, bluetoothDevice);
            }
            Log.i(TAG, "END acceptThread ");
        }
        //To close the serversocket
        public void cancel() {
            LogMessage("cancel: Canceling AcceptThread.");
            try {
                serverSocket.close();
            } catch (IOException e) {
                Log.e(TAG, "cancel: Close of AcceptThread ServerSocket failed. " + e.getMessage() );
            }
        }
    }


    /**
     * This thread runs while attempting to make an outgoing connection
     * with a device. It runs straight through; the connection either
     * succeeds or fails.
     */
    private class ConnectThread extends Thread {
        private BluetoothSocket bluetoothSocket;

        public ConnectThread(BluetoothDevice device, UUID uuid) {
            LogMessage("ConnectThread: start");
            bluetoothDevice = device;
            deviceUUID = uuid;
        }

        public void run(){
            BluetoothSocket tmp = null;
            Log.i(TAG, "ConnectThread: run");

            try {
                //get bluetooth socket
                tmp = bluetoothDevice.createRfcommSocketToServiceRecord(deviceUUID);
                Log.i(TAG, deviceUUID.toString() + " | " + MY_UUID);
            } catch (IOException e) {
                Log.e(TAG, "ConnectThread: Could not create InsecureRfcommSocket " + e.getMessage());
            }
            bluetoothSocket= tmp;

            //Cancel discovery cos it slows down a connection
            bluetoothAdapter.cancelDiscovery();

            // Make a connection to the BluetoothSocket
            try {
                //Is a blocking call, only returns on successful connection or an exception
                bluetoothSocket.connect();
                LogMessage("run: ConnectThread connected.");
                connected(bluetoothSocket, bluetoothDevice);
            } catch (IOException e) {
                try {
                    bluetoothSocket.close();
                    LogMessage("run: Closed Socket.");
                } catch (IOException e1) {
                    e.printStackTrace();
                    Log.e(TAG, "mConnectThread: run: Unable to close connection in socket " + e1.getMessage());
                }
                LogMessage("run: ConnectThread: Could not connect to UUID: " + MY_UUID);

                try {
                    MainActivity mainActivity = (MainActivity) context;
                    mainActivity.runOnUiThread(() -> Toast.makeText(context,
                            "Failed to connect to the Device.", Toast.LENGTH_SHORT).show());

                } catch (Exception z) {
                    z.printStackTrace();
                }

            }
            try {
                progressDialog.dismiss();
            } catch (NullPointerException e){
                e.printStackTrace();
            }
            Log.i(TAG, bluetoothSocket.toString() + " | " + bluetoothDevice.toString());
        }
        public void cancel() {
            try {
                LogMessage("cancel: Closing Client Socket.");
                bluetoothSocket.close();
            } catch (IOException e) {
                Log.e(TAG, "cancel: close() of Socket in Connectthread failed. " + e.getMessage());
            }
        }
    }

    /**
     * Start the service. Specifically start AcceptThread to begin a
     * session in listening (server) mode. Called by the Activity onResume()
     */
    public synchronized void start() {
        LogMessage("start");

        // Cancel any thread attempting to make a connection
        if (connectThread != null) {
            connectThread.cancel();
            connectThread = null;
        }
        if (acceptThread == null) {
            acceptThread = new AcceptThread();
            acceptThread.start();
        }
        //Accept Thread starts and waits for a connection
    }

    public void startClient(BluetoothDevice device, UUID uuid){
        LogMessage("startClient: Started.");

        try {
            this.progressDialog = new ProgressDialog(this.context);
            this.progressDialog.setTitle("Connecting Bluetooth");
            this.progressDialog.setMessage("Please wait...");
            this.progressDialog.setCancelable(false);
            this.progressDialog.setButton(
                    DialogInterface.BUTTON_NEGATIVE,
                    "Cancel",
                    (dialog, which) -> dialog.dismiss()
            );
            progressDialog.show();
        } catch (Exception e) {
            Log.e(TAG, "Error creating progressDialog " + e.getMessage());
        }

        connectThread = new ConnectThread(device, uuid);
        connectThread.start();
    }

    private class ConnectedThread extends Thread {
        private final BluetoothSocket bluetoothSocket;
        private final InputStream btInStream;
        private final OutputStream btOutStream;

        public ConnectedThread(BluetoothSocket socket) {
            LogMessage("ConnectedThread: Starting.");

            bluetoothSocket = socket;
            InputStream tmpIn = null;
            OutputStream tmpOut = null;

            try {
                LogMessage("GETTING INPUT STREAM");
                tmpIn = bluetoothSocket.getInputStream();
                LogMessage("GETTING OUTPUT STREAM");
                tmpOut = bluetoothSocket.getOutputStream();
            } catch (IOException e) {
                e.printStackTrace();
            }

            //send intent to update Connection Status
            Intent connStatus = new Intent("ConnectionStatus");
            connStatus.putExtra("Status", "connected");
            connStatus.putExtra("Device", bluetoothDevice);
            LocalBroadcastManager.getInstance(context).sendBroadcast(connStatus);
            isConnected = true;
            LogMessage("CONNECTED: " + isConnected);

            btInStream = tmpIn;
            btOutStream = tmpOut;
        }

        public void run(){
            byte[] buffer = new byte[1024];  // buffer store for the stream

            int bytes; // bytes returned from read()

            // Keep listening to the InputStream until an exception occurs
            while (true) {
                // Read from the InputStream
                try {
                    bytes = btInStream.read(buffer);
                    LogMessage("reading buffer");
                    String incomingMessage = new String(buffer, 0, bytes);
                    LogMessage("InputStream: " + incomingMessage);
                    incomingBTMessageHandler(incomingMessage);

                } catch (IOException e) {
                    Intent connStatus = new Intent("ConnectionStatus");
                    connStatus.putExtra("Status", "disconnected");
                    connStatus.putExtra("Device", bluetoothDevice);
                    isConnected = false;
                    LocalBroadcastManager.getInstance(context).sendBroadcast(connStatus);
                    Log.e(TAG, "write: Error reading Input Stream. " + e.getMessage() );
                    try {
                        bluetoothSocket.close();
                        break;
                    } catch (IOException e1) {
                        Log.e(TAG, "write: Error closing socket. " + e1.getMessage());
                        break;
                    }
                } catch (JSONException e){
                    Log.e(TAG, "JSON Error in incoming BT Message Handling");
                }
            }
        }

        //Call this from the main activity to send data to the remote device
        public void write(byte[] bytes) {
            String text = new String(bytes, Charset.defaultCharset());
            LogMessage("write: Writing to outputstream: " + text);
            try {
                btOutStream.write(bytes);
            } catch (IOException e) {
                Log.e(TAG, "write: Error writing to output stream. " + e.getMessage() );
            }
        }

        /* Call this from the main activity to shutdown the connection */
        public void cancel() {
            try {
                bluetoothSocket.close();
            } catch (IOException e) {
                Log.e(TAG, "write: Error closing ConnectThread socket. " + e.getMessage());
            }
        }
    }

    private void connected(BluetoothSocket socket, BluetoothDevice device) {
        LogMessage("connected: Starting.");

        // Stop AcceptThread cos only want to connect to 1 device
        if (acceptThread != null) {
            acceptThread.cancel();
            acceptThread = null;
        }

        // Start the thread to manage the connection and perform transmissions
        connectedThread = new ConnectedThread(socket);
        LogMessage("BLUETOOTH SOCKET CONNECTED:" + socket.isConnected());
        connectedThread.start();
    }


    /**
     * Write to connected thread in unsynchronized manner
     * @param out
     */
    public static void write(byte[] out) {
        // Create temporary object
        ConnectedThread r;

        // Synchronize a copy of the ConnectedThread
        Log.d(TAG, "write: Write called to " + connectedThread.toString());
        connectedThread.write(out);
    }

    private void incomingBTMessageHandler(String message) throws JSONException {
        Log.i(TAG, "incomingBTMessageHandler: New incoming message: " + message);

        //for checklist remove after
//        String tempMsg = message.substring(0,message.length());
//        String formattedInstruction = tempMsg.replaceAll("\\s", "");
//        List<String> instructionList = Arrays.asList(formattedInstruction.split(","));
//        String prefix = instructionList.get(0);
//        prefix = prefix.toUpperCase();
//        if (prefix.equals("TARGET")) {
//            message = String.format("{\"cat\": \"image-rec\", \"value\": {\"obstacle_id\": \"%s\", \"image_id\": \"%s\"}}", instructionList.get(1), instructionList.get(2));
//        } else if (prefix.equals("ROBOT")) {
//            String directionStr = "";
//            if(instructionList.get(3).equals("N")){
//                directionStr = "0";
//            } else if (instructionList.get(3).equals("E")) {
//                directionStr = "2";
//            }else if (instructionList.get(3).equals("S")) {
//                directionStr = "4";
//            }else if (instructionList.get(3).equals("W")) {
//                directionStr = "6";
//            }
//
//            message = String.format("{\"cat\": \"location\", \"value\": {\"x\": \"%s\", \"y\":\"%s\", \"d\":\"%s\"}}", instructionList.get(1), instructionList.get(2), directionStr);
//        }

        //end remove
        try{

            JSONObject messageJSON = new JSONObject(message);
            String msgType = messageJSON.getString("cat");
            switch(msgType.toUpperCase()){
                case "INFO":
                    //updates robot status textview
                    //for real time updates
                    //e.g {"cat":"info","value":"Ready to start"}
                    String infoStr = messageJSON.getString("value");
                    sendMsgIntent("updateRobocarStatus", infoStr);
                    return;
                case "IMAGE-REC":
                    //updates obstacle image text
                    //e.g {"cat": "image-rec", "value": {"obstacle_id": "1", "image_id": "11"}}
                    JSONObject imageRecObj = messageJSON.getJSONObject("value");
                    sendMsgIntent("imageResult", imageRecObj.toString());
                    return;
                case "LOCATION":
                    //updates robot location
                    //to see robot moving in real time
                    //e.g {"cat": "location", "value": {"x": "3", "y":"4", "d":"0"}}
                    //d0: up, 2:right, 4:down, 6:left
                    JSONObject locationObj = messageJSON.getJSONObject("value");
                    sendMsgIntent("updateRobocarLocation", locationObj.toString());
                    return;
                case "MODE":
                    //current unused todo remove
                    String mode = messageJSON.getString("value");
                    sendMsgIntent("updateRobocarMode", mode);
                    return;
                case "STATUS":
                    //status of robot
                    //e.g when robot is finished, then will stop timer
                    //if sent running then rest of buttons disabled
                    //{"cat":"status", "value":"finished"}

                    String status = messageJSON.getString("value");
                    sendMsgIntent("updateRobocarState", status);
                default:
                    String messageReceived = messageJSON.getString("value");
                    sendMsgIntent("incomingBTMessage", messageReceived);
            }
        }catch (Exception e){
            //Means its NOT a JSON Obj
            //if finish for task 2
            //todo check if error
            if (message.equals("FINISH/PATH")){
                sendMsgIntent("updateRobocarState", "finished");
            }
            else {
                //anything else
                sendMsgIntent("incomingBTMessage", message);
            }

        }
        plainTextCommandHandler(message);
    }

    //not impt, mainly use json so plaintext can ignore todo remove

    private void plainTextCommandHandler(String commandText){

        //NOT a JSON Object, so assume its basic text command responses
        try{
            if(commandText.contains("TARGET")){
                // Submitting target ID (imageResult)
                // TARGET, <Obstacle Number>, <Target ID>
                String[] commandComponents = commandText.split(",");
                if(commandComponents.length < 3){
                    Log.e(TAG, "incomingBTMessageHandler: The TARGET plain text command has insufficient parts, command: " + commandText);
                    return;
                }
                JSONObject imageRecResultObj = new JSONObject();
                imageRecResultObj.put("obstacle_id", commandComponents[1]);
                imageRecResultObj.put("image_id", commandComponents[2]);
                sendMsgIntent("imageResult", imageRecResultObj.toString());
                return;
            }
            if(commandText.contains("ROBOT")){
                //Submitting robot position update
                //ROBOT, <x>, <y>, <direction>
                String[] commandComponents = commandText.split(",");
                if(commandComponents.length < 4){
                    Log.e(TAG, "incomingBTMessageHandler: The ROBOT plain text command has insufficient parts, command: "+commandText);
                    return;
                }
                int xPos = Integer.parseInt(commandComponents[1]);
                int yPos = Integer.parseInt(commandComponents[2]);
                int dir = -1;
                switch(commandComponents[3].trim().toUpperCase()){
                    case "N":
                        dir = 0;
                        break;
                    case "E":
                        dir = 2;
                        break;
                    case "S":
                        dir = 4;
                        break;
                    case "W":
                        dir = 6;
                        break;
                }

                JSONObject positionJson = new JSONObject();
                positionJson.put("x", ++xPos);
                positionJson.put("y", ++yPos);
                positionJson.put("d", dir);
                sendMsgIntent("updateRobocarLocation", positionJson.toString());
            }
            Log.i(TAG, "plainTextCommandHandler: Unknown Command: "+commandText);
        }catch (Exception e){
            Log.e(TAG, "incomingBTMessageHandler: An error occurred while trying to handle plain text cmd");
            e.printStackTrace();
        }
    }

    private void sendMsgIntent(String intentAction, String content){
        Intent sendingIntent = new Intent(intentAction);
        sendingIntent.putExtra("msg", content);
        LocalBroadcastManager.getInstance(context).sendBroadcast(sendingIntent);
    }

    private void LogMessage(String message) {
        Log.d(TAG, message);
    }

    public synchronized void disconnect(){
        if(connectedThread != null){
            connectedThread.cancel();
            connectedThread = null;
        }
        if(connectThread != null){
            connectThread.cancel();
            connectThread = null;
        }
        if(acceptThread != null){
            acceptThread.cancel();
            acceptThread = null;
        }

        isConnected = false;
    }





}
