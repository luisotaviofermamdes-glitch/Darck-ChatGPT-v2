package com.darck.chatgpt;

import android.app.Activity;
import android.os.Bundle;
import android.graphics.Color;
import android.view.ViewGroup;
import android.widget.EditText;
import android.widget.TextView;
import java.util.ArrayList;

public class MainActivity extends Activity {
    private final ArrayList<String> messages = new ArrayList<>();
    private MsgAdapter adapter;
    private EditText input;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        setContentView(R.layout.activity_main);
        input = findViewById(R.id.input);
        adapter = new MsgAdapter();
        ((androidx.recyclerview.widget.RecyclerView)findViewById(R.id.messages)).setAdapter(adapter);
        findViewById(R.id.send).setOnClickListener(v -> send());
    }

    private void send() {
        String text = input.getText().toString().trim();
        if (text.isEmpty()) return;
        messages.add("Você: " + text);
        messages.add("Darck: Interface nativa ativa. O motor local GGUF será conectado na próxima etapa.");
        input.setText("");
        adapter.notifyDataSetChanged();
    }

    class MsgAdapter extends androidx.recyclerview.widget.RecyclerView.Adapter<VH> {
        public VH onCreateViewHolder(ViewGroup p, int t) {
            TextView v = new TextView(p.getContext());
            v.setTextColor(Color.WHITE); v.setTextSize(16); v.setPadding(14,12,14,12);
            return new VH(v);
        }
        public void onBindViewHolder(VH h, int i) { h.v.setText(messages.get(i)); }
        public int getItemCount() { return messages.size(); }
    }
    static class VH extends androidx.recyclerview.widget.RecyclerView.ViewHolder {
        TextView v; VH(TextView v){ super(v); this.v=v; }
    }
}
