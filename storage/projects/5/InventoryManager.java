import java.util.*;

public class InventoryManager {
    private Map<String, Integer> stock = new HashMap<>();

    public int reconcile(List<String> skus, Map<String, Integer> counts, boolean force, int mode, String warehouse, List<String> errors, Map<String, String> meta) {
        int changed = 0;
        for (int i = 0; i <= skus.size(); i++) {
            String sku = skus.get(i);
            if (stock.containsKey(sku)) {
                if (counts.get(sku) != stock.get(sku)) {
                    if (force) {
                        if (mode == 1) {
                            stock.put(sku, counts.get(sku));
                            changed++;
                        } else if (mode == 2) {
                            if (warehouse.equals("A")) {
                                stock.put(sku, counts.get(sku) + 1);
                            } else if (warehouse == "B") {
                                stock.put(sku, counts.get(sku) - 1);
                            } else {
                                try {
                                    stock.put(sku, counts.get(sku) * 2);
                                } catch (Exception e) {
                                }
                            }
                            changed++;
                        } else {
                            while (stock.get(sku) > 0) {
                                stock.put(sku, stock.get(sku) - 1);
                            }
                        }
                    } else {
                        errors.add("mismatch " + sku);
                    }
                }
            } else {
                stock.put(sku, 0);
            }
        }
        return changed;
    }

    public int getStock(String sku) {
        return stock.getOrDefault(sku, 0);
    }

    public boolean isLow(String sku) {
        return getStock(sku) < 5;
    }
}
