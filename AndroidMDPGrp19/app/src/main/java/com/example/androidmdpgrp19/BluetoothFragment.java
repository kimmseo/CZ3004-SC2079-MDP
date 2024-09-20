package com.example.androidmdpgrp19;

import android.Manifest;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.app.ProgressDialog;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;

import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.fragment.app.Fragment;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;

import android.os.Handler;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.Objects;
import java.util.Set;
import java.util.UUID;

public class BluetoothFragment extends Fragment {

    // the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
    private static final String ARG_PARAM1 = "param1";
    private static final String ARG_PARAM2 = "param2";

    private boolean isBluetoothOn;

    //from main

    BluetoothAdapter bluetoothAdapter;
    ListView pairedDeviceListView;
    ListView availDeviceListView;

    TextView btConnStatusTextView;
    TextView btConnDeviceNameTextView;

    Button btToggleButton;
    Button btFindDevicesButton;

    Button connectButton;

    TextView btMessagesTextView;
    EditText inputMsgEditText;
    Button sendButton;
    Button manualButton;
    Button pathButton;

    private String TAG = "Bluetooth Fragment";

    public ArrayList<BluetoothDevice> availDevicesArrList = new ArrayList<>();
    public ArrayList<BluetoothDevice> pairedDevicesArrList = new ArrayList<>();
    public BluetoothDeviceListAdapter availDeviceListAdapter;
    public BluetoothDeviceListAdapter pairedDeviceListAdapter;

    BluetoothDevice myBTDevice;

    BluetoothConnectionService bluetoothConnectionService;
    private static final UUID MY_UUID = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB");

    private ProgressDialog btDisconnectProgressDialog;
    private boolean retryConnection = false;

    Handler reconnectionHandler = new Handler();

    public BluetoothFragment() {
        isBluetoothOn = false;
    }

    public static BluetoothFragment newInstance(String param1, String param2) {
        BluetoothFragment fragment = new BluetoothFragment();
        Bundle args = new Bundle();
        args.putString(ARG_PARAM1, param1);
        args.putString(ARG_PARAM2, param2);
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        View fragView = inflater.inflate(R.layout.bluetooth_fragment_layout, container, false);

        pairedDeviceListView = fragView.findViewById(R.id.pairedDeviceList);
        availDeviceListView = fragView.findViewById(R.id.availDeviceList);

        btConnStatusTextView = fragView.findViewById(R.id.bluetoothConnStatus);
        btConnDeviceNameTextView = fragView.findViewById(R.id.bluetoothConnDeviceName);

        btToggleButton = fragView.findViewById(R.id.bluetoothToggleBtn);
        btFindDevicesButton = fragView.findViewById(R.id.findDevicesBtn);
        connectButton = fragView.findViewById(R.id.connectBtn);

        btMessagesTextView = fragView.findViewById(R.id.btMessagesTextView);
        inputMsgEditText = fragView.findViewById(R.id.inputMsgEditText);
        sendButton = fragView.findViewById(R.id.sendBtn);

        manualButton = fragView.findViewById(R.id.manual_mode_toggle);
        pathButton = fragView.findViewById(R.id.path_mode_toggle);
        //path is default enabled

        initBluetooth();

        pairedDeviceListView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @SuppressLint("MissingPermission")
            @Override
            public void onItemClick(AdapterView<?> adapterView, View view, int i, long l) {
                bluetoothAdapter.cancelDiscovery();
                availDeviceListView.setAdapter(availDeviceListAdapter);

                String deviceName = pairedDevicesArrList.get(i).getName();
                String deviceAddress = pairedDevicesArrList.get(i).getAddress();
                Log.d(TAG, "onItemClick: A device is selected.");
                Log.d(TAG, "onItemClick: DEVICE NAME: " + deviceName);
                Log.d(TAG, "onItemClick: DEVICE ADDRESS: " + deviceAddress);

                bluetoothConnectionService = new BluetoothConnectionService(getContext());
                myBTDevice = pairedDevicesArrList.get(i);
            }
        });

        availDeviceListView.setOnItemClickListener(
                new AdapterView.OnItemClickListener() {
                    @Override
                    public void onItemClick(AdapterView<?> adapterView, View view, int i, long l) {

                        //CANCEL DEVICE SEARCH DISCOVERY
                        if (ActivityCompat.checkSelfPermission(getContext(), Manifest.permission.BLUETOOTH_SCAN) != PackageManager.PERMISSION_GRANTED) {
                            // TODO: Consider calling
                            //    ActivityCompat#requestPermissions
                            // here to request the missing permissions, and then overriding
                            //   public void onRequestPermissionsResult(int requestCode, String[] permissions,
                            //                                          int[] grantResults)
                            // to handle the case where the user grants the permission. See the documentation
                            // for ActivityCompat#requestPermissions for more details.
                        }
                        bluetoothAdapter.cancelDiscovery();

                        Log.d(TAG, "onItemClick: Item Selected");

                        String deviceName = availDevicesArrList.get(i).getName();
                        String deviceAddress = availDevicesArrList.get(i).getAddress();

                        //UnSelect Paired Device List
                        pairedDeviceListView.setAdapter(pairedDeviceListAdapter);


                        Log.d(TAG, "onItemClick: DeviceName = " + deviceName);
                        Log.d(TAG, "onItemClick: DeviceAddress = " + deviceAddress);

                        if (Build.VERSION.SDK_INT > Build.VERSION_CODES.JELLY_BEAN_MR2) {
                            Log.d(TAG, "onItemClick: Initiating pairing with " + deviceName);
                            availDevicesArrList.get(i).createBond();

                            bluetoothConnectionService = new BluetoothConnectionService(getContext());
                            myBTDevice = availDevicesArrList.get(i);
                        }

                    }
                }
        );

        btToggleButton.setOnClickListener(view -> {
            //onBluetooth(view);
            toggleBluetooth();
        });

        btFindDevicesButton.setOnClickListener(view -> {
            discoverDevices(view);
        });

        connectButton.setOnClickListener(view -> {
            if(myBTDevice ==null)
            {
                Toast.makeText(getActivity(), "Please Select a Device before connecting.", Toast.LENGTH_SHORT).show();
            }
            else {
                startBTConnection(myBTDevice, MY_UUID);
            }
        });

        sendButton.setOnClickListener(view -> {
            String sentText = "" + this.inputMsgEditText.getText().toString();
            this.btMessagesTextView.append(sentText + "\n");
            this.inputMsgEditText.setText("");

            if (BluetoothConnectionService.isConnected) {
                byte[] bytes = sentText.getBytes(Charset.defaultCharset());
                BluetoothConnectionService.write(bytes);
            }
        });

        manualButton.setOnClickListener(v -> {
            manualButton.setEnabled(true);
            pathButton.setEnabled(false);
            sendIntent("updateRobocarMode", "manual");
        });

        pathButton.setOnClickListener(v -> {
            pathButton.setEnabled(true);
            manualButton.setEnabled(false);
            sendIntent("updateRobocarMode", "path");
        });


        // pops up when BT is disconnected
        this.btDisconnectProgressDialog = new ProgressDialog(getContext());
        this.btDisconnectProgressDialog.setMessage("Bluetooth Disconnected. Waiting for other device to reconnect...");
        this.btDisconnectProgressDialog.setCancelable(false);
        this.btDisconnectProgressDialog.setButton(
                DialogInterface.BUTTON_NEGATIVE,
                "Cancel",
                (dialog, which) -> dialog.dismiss()
        );


        return fragView;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Register for broadcasts when a device is discovered.
        IntentFilter filter = new IntentFilter(BluetoothDevice.ACTION_FOUND);
        getActivity().registerReceiver(discoverBroadcastReceiver, filter);

        //incoming message broadcast receiver
        LocalBroadcastManager.getInstance(getContext()).registerReceiver(incomingMsgReceiver, new IntentFilter("incomingBTMessage"));

        //send bt message receiver
        LocalBroadcastManager.getInstance(getContext()).registerReceiver(sendBTMsgReceiver, new IntentFilter("sendBTMessage"));

    }

    @Override
    public void onResume() {
        super.onResume();
        try {
            IntentFilter connStatusIntentFilter = new IntentFilter("ConnectionStatus");
            LocalBroadcastManager.getInstance(getContext()).registerReceiver(connStatusBroadcastReceiver, connStatusIntentFilter);
        } catch (IllegalArgumentException e) {
            e.printStackTrace();
        }
    }

    //TODO add more to initBluetooth
    private void initBluetooth() {
        bluetoothAdapter = BluetoothAdapter.getDefaultAdapter();
        if (bluetoothAdapter == null) {
            displayShortToast("Bluetooth is not supported on this device");
        }
        if (bluetoothAdapter.isEnabled()) {
            isBluetoothOn = true;
        }

        updateBTButtons();
        findPairedDevices();
    }

    private void findPairedDevices() {
        Set<BluetoothDevice> bluetoothDeviceSet = bluetoothAdapter.getBondedDevices();
        String[] pairedDeviceNameArr = new String[bluetoothDeviceSet.size()];

        if (bluetoothDeviceSet.size() > 0) {
            for (BluetoothDevice device : bluetoothDeviceSet) {
                pairedDevicesArrList.add(device);
            }
        }

//        if (pairedDevices.size() > 0) {
//            // There are paired devices. Get the name and address of each paired device.
//            for (BluetoothDevice device : pairedDevices) {
//                String deviceName = device.getName();
//                String deviceHardwareAddress = device.getAddress(); // MAC address
//            }
//        }

        pairedDeviceListAdapter = new BluetoothDeviceListAdapter(getContext(), R.layout.btdevice, pairedDevicesArrList);
        pairedDeviceListView.setAdapter(pairedDeviceListAdapter);

//        pairedDeviceArrAdapter = new ArrayAdapter<String>(getApplicationContext(), android.R.layout.simple_list_item_1, pairedDeviceNameArr);
//        pairedDeviceListView.setAdapter(pairedDeviceArrAdapter);
    }

    public void discoverDevices(View v) {
        checkLocationPermission();


        Intent discoverableIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_DISCOVERABLE);
        discoverableIntent.putExtra(BluetoothAdapter.EXTRA_DISCOVERABLE_DURATION, 300);
        startActivity(discoverableIntent);

        bluetoothAdapter.startDiscovery();
    }

    public void onBluetooth(View v) {
        if (!bluetoothAdapter.isEnabled()) {
            Intent i = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
            activityResultLauncher.launch(i);
        }
    }

    public void checkBTPermissions() {
        if ((ContextCompat.checkSelfPermission(getContext(), android.Manifest.permission.BLUETOOTH_CONNECT) == PackageManager.PERMISSION_GRANTED) &&
                (ContextCompat.checkSelfPermission(getContext(), android.Manifest.permission.BLUETOOTH_SCAN) == PackageManager.PERMISSION_GRANTED)) {
            return;
        }
        requestPermissionLauncher.launch(android.Manifest.permission.BLUETOOTH_CONNECT);
        requestPermissionLauncher.launch(android.Manifest.permission.BLUETOOTH_SCAN);
    }

    public void checkLocationPermission() {
        if (ContextCompat.checkSelfPermission(getContext(), android.Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED
                && ContextCompat.checkSelfPermission(getContext(), android.Manifest.permission.ACCESS_COARSE_LOCATION) == PackageManager.PERMISSION_GRANTED) {
            return;
        }
        displayShortToast("Please grant locations permissions first!");

        requestPermissionLauncher.launch(android.Manifest.permission.ACCESS_FINE_LOCATION);
        requestPermissionLauncher.launch(android.Manifest.permission.ACCESS_COARSE_LOCATION);
    }

    public void startBTConnection(BluetoothDevice device, UUID uuid){
        Log.d(TAG, "startBTConnection: Initializing RFCOM Bluetooth Connection");
        bluetoothConnectionService.startClient(device, uuid);
    }

    private void toggleBluetooth() {
        //Toggle the status
        isBluetoothOn = !isBluetoothOn;
        if (isBluetoothOn) {
            bluetoothAdapter.enable();
        } else {
            bluetoothAdapter.disable();
        }
        updateBTButtons();
    }

    private void updateBTButtons() {
        if (isBluetoothOn) {
            btToggleButton.setText("Bluetooth ON");
            btToggleButton.setEnabled(true);
            btFindDevicesButton.setEnabled(true);
        } else {
            btToggleButton.setText("Bluetooth OFF");
            btToggleButton.setEnabled(false);
            btFindDevicesButton.setEnabled(false);
        }
    }

    private void disconnectBluetooth(){
        bluetoothConnectionService.disconnect();
    }

    // Create a BroadcastReceiver for ACTION_FOUND.
    private final BroadcastReceiver discoverBroadcastReceiver = new BroadcastReceiver() {
        public void onReceive(Context context, Intent intent) {
            String action = intent.getAction();
            if (BluetoothDevice.ACTION_FOUND.equals(action)) {
                // Discovery has found a device. Get the BluetoothDevice
                // object and its info from the Intent.
                BluetoothDevice device = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE);

                //check if btDevice has been added yet
                boolean isDeviceAlrAdded = false;
                for (BluetoothDevice availDevice : availDevicesArrList) {
                    // Objects.equals() for null-safe comparison and check device address
                    if (Objects.equals(availDevice.getAddress(), device.getAddress())) {
                        isDeviceAlrAdded = true;
                        break;
                    }
                }

                //device not added so add now
                if(!isDeviceAlrAdded){
                    availDevicesArrList.add(device);
                }

                //availDevicesArrList.add(device);
                if (ActivityCompat.checkSelfPermission(getContext(), Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) {
                    //request permissions
                    checkBTPermissions();
                    return;
                }
                availDeviceListAdapter = new BluetoothDeviceListAdapter(getContext(), R.layout.btdevice, availDevicesArrList);
                availDeviceListView.setAdapter(availDeviceListAdapter);

                //TODO filter for duplicate devices, check if works

//
            }
        }
    };

    //Connection Status Receiver
    private final BroadcastReceiver connStatusBroadcastReceiver = new BroadcastReceiver() {
        public void onReceive(Context context, Intent intent) {
            BluetoothDevice btDevice = intent.getParcelableExtra("Device");
            String btStatus = intent.getStringExtra("Status");
            String btDeviceName = btDevice.getName();

            if (btStatus.equals("connected")) {
                try {
                    btDisconnectProgressDialog.dismiss();
                } catch (NullPointerException e) {
                    e.printStackTrace();
                }
                displayShortToast("Device now connected to " + btDeviceName);
                //update Connection Status Texts
                btConnStatusTextView.setText("Connected");
                btConnStatusTextView.setTextColor(ContextCompat.getColor(getContext(), R.color.green));
                btConnDeviceNameTextView.setText(btDeviceName);
                retryConnection = false;

                //update robot state

            } else if (btStatus.equals("disconnected")) {
                displayShortToast("Disconnected from " + btDeviceName);
                btConnStatusTextView.setText("Disconnected");
                btConnStatusTextView.setTextColor(ContextCompat.getColor(getContext(), R.color.red));
                btConnDeviceNameTextView.setText("Device");
                btDisconnectProgressDialog.show();
                retryConnection = true;
                reconnectionHandler.postDelayed(reconnectionRunnable, 5000);
            }
        }
    };

    //Incoming message Receiver
    private final BroadcastReceiver incomingMsgReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            String text = intent.getStringExtra("msg");
            if (text != null) {
                btMessagesTextView.append(text + "\n");
            } else {
                Log.d(TAG, "Received intent without 'receivedMessage' extra or it is null");
            }
        }

    };

    //Send message over BT Receiver
    private BroadcastReceiver sendBTMsgReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            String msg = intent.getStringExtra("msg");
            try{
                byte[] msgInBytes = msg.getBytes(Charset.defaultCharset());
                bluetoothConnectionService.write(msgInBytes);
            }catch(Exception e){
                Log.e(TAG,"An error occurred while sending bluetooth message");
                e.printStackTrace();
            }
        }
    };

    private void sendIntent(String intentAction, String content){
        Intent sendingIntent = new Intent(intentAction);
        sendingIntent.putExtra("msg", content);
        LocalBroadcastManager.getInstance(getContext()).sendBroadcast(sendingIntent);
    }

    private ActivityResultLauncher<Intent> activityResultLauncher = registerForActivityResult(
            new ActivityResultContracts.StartActivityForResult(),
            result -> {
                if (result.getResultCode() == Activity.RESULT_OK) {
                    // There are no request codes
                    displayShortToast("Bluetooth now Enabled");
                }
            });

    private ActivityResultLauncher<String> requestPermissionLauncher =
            registerForActivityResult(new ActivityResultContracts.RequestPermission(), isGranted -> {
                if (isGranted) {
                    displayShortToast("Permission granted");
                } else {
                    displayShortToast("Please give Permissions");
                }
            });



    Runnable reconnectionRunnable = new Runnable() {
        @Override
        public void run() {
            try {
                if (BluetoothConnectionService.isConnected == false && retryConnection) {
                    startBTConnection(myBTDevice, MY_UUID);
                    displayShortToast("Reconnection Success");
                }
                reconnectionHandler.removeCallbacks(reconnectionRunnable);
                retryConnection = false;
            } catch (Exception e) {
                displayShortToast("Failed to reconnect, trying in 5 second");
            }
        }
    };

    private void displayShortToast(String message) {
        Toast.makeText(getActivity(), message, Toast.LENGTH_LONG).show();
    }
}