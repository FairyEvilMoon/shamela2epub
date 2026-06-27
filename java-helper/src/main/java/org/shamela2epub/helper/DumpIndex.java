package org.shamela2epub.helper;

import java.io.BufferedWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

import org.apache.lucene.document.Document;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.store.FSDirectory;

public class DumpIndex {
    static class Entry {
        String id;
        String body;
        Entry(String id, String body) { this.id = id; this.body = body; }
    }

    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            throw new IllegalArgumentException("Usage: DumpIndex <indexPath> <kind> <outputJson> [bookId]");
        }
        Path indexPath = Path.of(args[0]);
        String kind = args[1];
        Path output = Path.of(args[2]);
        String bookId = args.length >= 4 ? args[3] : null;

        List<Entry> entries = new ArrayList<>();
        try (DirectoryReader reader = DirectoryReader.open(FSDirectory.open(indexPath))) {
            for (int i = 0; i < reader.maxDoc(); i++) {
                Document doc = reader.document(i);
                String rawId = doc.get("id");
                String body = doc.get("body");
                if (rawId == null || body == null) continue;

                String id = rawId;
                if (bookId != null && !bookId.isBlank()) {
                    String prefix = bookId + "-";
                    if (!rawId.startsWith(prefix)) continue;
                    id = rawId.substring(prefix.length());
                }
                entries.add(new Entry(id, body));
            }
        }

        entries.sort(Comparator.comparingInt(e -> safeInt(e.id)));
        Files.createDirectories(output.toAbsolutePath().getParent());
        try (BufferedWriter out = Files.newBufferedWriter(output, StandardCharsets.UTF_8)) {
            out.write("{\"kind\":"); out.write(json(kind)); out.write(",\"documents\":{");
            boolean first = true;
            for (Entry e : entries) {
                if (!first) out.write(",");
                first = false;
                out.write(json(e.id)); out.write(":"); out.write(json(e.body));
            }
            out.write("}}\n");
        }
    }

    static int safeInt(String s) {
        try { return Integer.parseInt(s); }
        catch (Exception e) { return Integer.MAX_VALUE; }
    }

    static String json(String s) {
        StringBuilder b = new StringBuilder();
        b.append('"');
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            switch (c) {
                case '"': b.append("\\\""); break;
                case '\\': b.append("\\\\"); break;
                case '\b': b.append("\\b"); break;
                case '\f': b.append("\\f"); break;
                case '\n': b.append("\\n"); break;
                case '\r': b.append("\\r"); break;
                case '\t': b.append("\\t"); break;
                default:
                    if (c < 0x20) b.append(String.format("\\u%04x", (int)c));
                    else b.append(c);
            }
        }
        b.append('"');
        return b.toString();
    }
}
