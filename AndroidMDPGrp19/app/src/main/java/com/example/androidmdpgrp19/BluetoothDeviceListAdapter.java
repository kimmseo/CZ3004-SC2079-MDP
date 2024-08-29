package com.example.androidmdpgrp19;

import android.bluetooth.BluetoothDevice;
import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.TextView;

import java.util.ArrayList;

public class BluetoothDeviceListAdapter extends ArrayAdapter<BluetoothDevice> {
    private LayoutInflater layoutInflater;
    private ArrayList<BluetoothDevice> bluetoothDevices;
    private int viewResourceId;

    public BluetoothDeviceListAdapter(Context context, int vResourceId, ArrayList<BluetoothDevice> devices){
        super(context, vResourceId,devices);
        this.bluetoothDevices = devices;
        layoutInflater = (LayoutInflater) context.getSystemService(Context.LAYOUT_INFLATER_SERVICE);
        viewResourceId = vResourceId;
    }

    public View getView(int position, View convertView, ViewGroup parent) {
        convertView = layoutInflater.inflate(viewResourceId, null);

        BluetoothDevice device = bluetoothDevices.get(position);

        if (device != null) {
            TextView deviceName = (TextView) convertView.findViewById(R.id.btDeviceName);
            TextView deviceAdress = (TextView) convertView.findViewById(R.id.btDeviceAddress);

            if (deviceName != null) {
                deviceName.setText(device.getName());
            }
            if (deviceAdress != null) {
                deviceAdress.setText(device.getAddress());
            }
        }

        return convertView;
    }
}
