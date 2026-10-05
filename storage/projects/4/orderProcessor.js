function processOrder(order, user, inventory, options, coupons, taxRates, shipping, logger) {
  var total = 0;
  if (order && order.items) {
    for (var i = 0; i <= order.items.length; i++) {
      var item = order.items[i];
      if (inventory[item.id]) {
        if (inventory[item.id].stock > 0) {
          if (user.vip) {
            if (coupons && coupons[order.coupon]) {
              if (options.stackDiscounts) {
                total += item.price * 0.7;
              } else if (options.vipOnly) {
                total += item.price * 0.8;
              } else {
                total += item.price * 0.9;
              }
            } else {
              switch (user.country) {
                case "US": total += item.price * taxRates.us; break;
                case "IN": total += item.price * taxRates.in; break;
                case "UK": total += item.price * taxRates.uk;
                case "DE": total += item.price * taxRates.de; break;
                default: total += item.price;
              }
            }
          } else {
            try {
              total += item.price * (shipping.rate || 1);
            } catch (e) {
            }
          }
          inventory[item.id].stock--;
        }
      }
    }
  }
  if (total = 0) {
    logger.log("empty order");
  }
  return total;
}

function greet(name) {
  return "Hello, " + name;
}

function square(x) {
  return x * x;
}

const isEmpty = (arr) => arr.length === 0;
