package com.example.androidmdpgrp19;

import android.app.ProgressDialog;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothServerSocket;
import android.bluetooth.BluetoothSocket;
import android.content.Context;
import android.content.Intent;
import android.util.Log;
import android.widget.Toast;

import androidx.localbroadcastmanager.content.LocalBroadcastManager;


import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.Charset;
import java.util.UUID;

public class BluetoothConnectionService {
    public static final String TAG = "BtConnectionSvc";
    private static final String appName = "MDP19Android";
    private static final UUID MY_UUID_INSECURE = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB");
    private final BluetoothAdapter bluetoothAdapter;
    Context context;
    private AcceptThread insecureAcceptThread;
    private ConnectThread connectThread;
    private static ConnectedThread connectedThread;

    private BluetoothDevice bluetoothDevice;
    private UUID deviceUUID;

    private ProgressDialog progressDialog;

    public static boolean isConnected = false;

    public BluetoothConnectionService(Context context){
        //context is Bluetooth page Context
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
        public AcceptThread(){
            BluetoothServerSocket temp = null;

            try{
                temp = bluetoothAdapter.listenUsingInsecureRfcommWithServiceRecord(appName, MY_UUID_INSECURE);
                Log.d(TAG, temp.toString());
                Log.d(TAG,"Setting up server using "+MY_UUID_INSECURE);
            }catch (IOException e){
                Log.e(TAG, "AcceptThread: IO Exception "+e.getMessage());
            }
            serverSocket = temp;
        }

        public void run(){
            Log.d(TAG, "AcceptThread: run");
            BluetoothSocket socket = null;
            try{
                Log.d(TAG, "run: RFCOM server socket start.....");
                // Blocking call, returns on a successful connection or an exception only
                Log.d(TAG, serverSocket.toString());
                socket = serverSocket.accept();
                Log.d(TAG, "run: RFCOM server socket accepted connection.");
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
            Log.d(TAG, "cancel: Canceling AcceptThread.");
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
            Log.d(TAG, "ConnectThread: start");
            bluetoothDevice = device;
            deviceUUID = uuid;
        }

        public void run(){
            BluetoothSocket tmp = null;
            Log.i(TAG, "ConnectThread: run");

            try {
                //get bluetooth socket
                tmp = bluetoothDevice.createRfcommSocketToServiceRecord(deviceUUID);
                Log.i(TAG, deviceUUID.toString() + " | " + MY_UUID_INSECURE);
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
                Log.d(TAG, "run: ConnectThread connected.");
                connected(bluetoothSocket, bluetoothDevice);
            } catch (IOException e) {
                try {
                    bluetoothSocket.close();
                    Log.d(TAG, "run: Closed Socket.");
                } catch (IOException e1) {
                    e.printStackTrace();
                    Log.e(TAG, "mConnectThread: run: Unable to close connection in socket " + e1.getMessage());
                }
                Log.d(TAG, "run: ConnectThread: Could not connect to UUID: " + MY_UUID_INSECURE );

                try {
                    //link to bluetooth page TODO
                    /*BluetoothPopUp mBluetoothPopUpActivity = (BluetoothPopUp) mContext;
                    mBluetoothPopUpActivity.runOnUiThread(() -> Toast.makeText(mContext,
                            "Failed to connect to the Device.", Toast.LENGTH_SHORT).show());*/
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
                Log.d(TAG, "cancel: Closing Client Socket.");
                bluetoothSocket.close();
            } catch (IOException e) {
                Log.e(TAG, "cancel: close() of mmSocket in Connectthread failed. " + e.getMessage());
            }
        }
    }

    /**
     * Start the service. Specifically start AcceptThread to begin a
     * session in listening (server) mode. Called by the Activity onResume()
     */
    public synchronized void start() {
        Log.d(TAG, "start");

        // Cancel any thread attempting to make a connection
        if (connectThread != null) {
            connectThread.cancel();
            connectThread = null;
        }
        if (insecureAcceptThread == null) {
            insecureAcceptThread = new AcceptThread();
            insecureAcceptThread.start();
        }
        //Accept Thread starts and waits for a connection
    }

    public void startClient(BluetoothDevice device, UUID uuid){
        Log.d(TAG, "startClient: Started.");

        try {
            this.progressDialog = ProgressDialog.show(this.context, "Connecting Bluetooth", "Please Wait...", true);
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
            Log.d(TAG, "ConnectedThread: Starting.");

            bluetoothSocket = socket;
            InputStream tmpIn = null;
            OutputStream tmpOut = null;

            try {
                Log.d(TAG, "GETTING INPUT STREAM");
                tmpIn = bluetoothSocket.getInputStream();
                Log.d(TAG, "GETTING OUTPUT STREAM");
                tmpOut = bluetoothSocket.getOutputStream();

                //send intent to update Connection Status
                Intent connStatus = new Intent("ConnectionStatus");
                connStatus.putExtra("Status", "connected");
                connStatus.putExtra("Device", bluetoothDevice);
                LocalBroadcastManager.getInstance(context).sendBroadcast(connStatus);
                isConnected = true;
                Log.d(TAG, "CONNECTED: " + isConnected);
            } catch (IOException e) {
                e.printStackTrace();
            }

            btInStream = tmpIn;
            btOutStream = tmpOut;
        }

        public void run(){
            byte[] buffer = new byte[1024];  // buffer store for the stream

            int bytes; // bytes returned from read()
            StringBuilder msgBuffer = new StringBuilder();

            // Keep listening to the InputStream until an exception occurs
            while (true) {
                // Read from the InputStream
                try {
                    bytes = btInStream.read(buffer);
                    Log.d(TAG, "reading buffer");
                    String incomingMessage = new String(buffer, 0, bytes);
                    Log.d(TAG, "InputStream: " + incomingMessage);
                    msgBuffer.append(incomingMessage);

                    int delimiterIndex = msgBuffer.indexOf("\n");
                    if (delimiterIndex != -1) {
                        String[] messages = msgBuffer.toString().split("\n");
                        for (String message : messages) {
                            Intent incomingMessageIntent = new Intent("incomingMessage");
                            incomingMessageIntent.putExtra("receivedMessage", message);

                            LocalBroadcastManager.getInstance(context).sendBroadcast(incomingMessageIntent);
                        }

                        // Reset the message buffer
                        msgBuffer = new StringBuilder();
                    }
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
                }
            }
        }
        //TODO see how to make BT instant reconnect after disconnect

        //Call this from the main activity to send data to the remote device
        public void write(byte[] bytes) {
            String text = new String(bytes, Charset.defaultCharset());
            Log.d(TAG, "write: Writing to outputstream: " + text);
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
        Log.d(TAG, "connected: Starting.");

        // Stop AcceptThread cos only want to connect to 1 device
        if (insecureAcceptThread != null) {
            insecureAcceptThread.cancel();
            insecureAcceptThread = null;
        }

        // Start the thread to manage the connection and perform transmissions
        connectedThread = new ConnectedThread(socket);
        Log.d(TAG, "BLUETOOTH SOCKET CONNECTED:" + socket.isConnected());
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





}
