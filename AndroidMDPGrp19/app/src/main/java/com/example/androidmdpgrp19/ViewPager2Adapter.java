package com.example.androidmdpgrp19;

import androidx.annotation.NonNull;
import androidx.fragment.app.Fragment;
import androidx.fragment.app.FragmentActivity;
import androidx.viewpager2.adapter.FragmentStateAdapter;

public class ViewPager2Adapter extends FragmentStateAdapter {
    private static final String[] TAB_TITLES = new String[]{ "Home", "Bluetooth"};

    public ViewPager2Adapter(@NonNull FragmentActivity fragmentActivity) {
        super(fragmentActivity);
    }

    @Override
    public Fragment createFragment(int position) {
        //return null;
        Fragment fragment = null;

        switch (position)
        {
            case 0:
                fragment = MainFragment.newInstance("", "");
                break;
            case 1:
                fragment = BluetoothFragment.newInstance("", "");
                break;

        }
        return fragment;
    }

    @Override
    public int getItemCount() {
        return TAB_TITLES.length;
    }
}
