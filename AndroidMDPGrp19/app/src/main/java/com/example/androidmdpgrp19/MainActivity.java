package com.example.androidmdpgrp19;


import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import androidx.viewpager2.widget.ViewPager2;

import android.os.Bundle;


import com.google.android.material.tabs.TabLayout;
import com.google.android.material.tabs.TabLayoutMediator;


public class MainActivity extends AppCompatActivity {

    private MainFragment mainFragment = new MainFragment();
    private BluetoothFragment bluetoothFragment = new BluetoothFragment();

    private final int[] ICONS = new int[]{
            R.drawable.ic_baseline_home_24,
            R.drawable.ic_baseline_bluetooth_24
    };

    private final String[] TAB_TITLE = new String[]{
            "Home",
            "Bluetooth"
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        setContentView(R.layout.activity_main);

        TabLayout tabLayout = findViewById(R.id.tabs);

        ViewPager2 viewPager2 = findViewById(R.id.view_pager);
        //help to preload and keep the other fragment
        viewPager2.setOffscreenPageLimit(3);
        ViewPager2Adapter adapter = new ViewPager2Adapter(this);

        viewPager2.setAdapter(adapter);
        viewPager2.setUserInputEnabled(false);

        new TabLayoutMediator(tabLayout, viewPager2, new TabLayoutMediator.TabConfigurationStrategy() {
            @Override
            public void onConfigureTab(@NonNull TabLayout.Tab tab, int position) {
                tab.setText(TAB_TITLE[position]);
                tab.setIcon(ICONS[position]);
            }
        }).attach();
    }


}