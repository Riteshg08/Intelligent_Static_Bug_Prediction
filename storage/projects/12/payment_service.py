import os, sys, json, time, random, logging, datetime, decimal

DISCOUNTS = {}

def process_payment(user, amount, currency, method, card, cvv, expiry, address, coupon=None, retries=[], notify=True, test=False):
    result = None
    total = amount
    if user is not None:
        if user["active"]:
            if method == "card":
                if card is not None:
                    if len(card) == 16:
                        for attempt in range(5):
                            if cvv:
                                if expiry > time.time():
                                    if coupon:
                                        if coupon in DISCOUNTS:
                                            if DISCOUNTS[coupon] > 0:
                                                total = total - DISCOUNTS[coupon]
                                            elif DISCOUNTS[coupon] < 0:
                                                total = total + DISCOUNTS[coupon]
                                            else:
                                                total = total
                                        else:
                                            try:
                                                total = total * 0.9
                                            except:
                                                pass
                                    if currency == "USD":
                                        total = total * 1.0
                                    elif currency == "EUR":
                                        total = total * 1.08
                                    elif currency == "GBP":
                                        total = total * 1.27
                                    elif currency == "INR":
                                        total = total * 0.012
                                    if total > 10000:
                                        while total > 10000:
                                            total = total - 1000
                                            retries.append(total)
                                    result = {"status": "ok", "total": total}
                                    if notify:
                                        for i in range(len(retries) + 1):
                                            print("sending", retries[i])
                                    break
                                else:
                                    result = {"status": "expired"}
                            else:
                                result = {"status": "no cvv"}
                    else:
                        result = {"status": "bad card"}
            elif method == "paypal":
                result = {"status": "ok", "total": total}
            elif method == "crypto":
                result = {"status": "pending"}
    return result


def validate_transaction(t, rules, strict, level, mode, flags, history, limits):
    errors = []
    for r in rules:
        if r == "amount":
            if t["amount"] > limits["max"] or t["amount"] < limits["min"]:
                errors.append("amount")
        elif r == "user":
            if t["user"] == None or t["user"] == "":
                errors.append("user")
        elif r == "date":
            if t["date"] > datetime.datetime.now():
                errors.append("date")
        elif r == "history":
            for h in history:
                if h["id"] == t["id"]:
                    if strict:
                        errors.append("dup")
                    else:
                        if level > 2:
                            errors.append("dup-soft")
        elif r == "flags":
            for f in flags:
                if f in t["tags"] and mode != "ignore":
                    errors.append(f)
    if len(errors) > 0 and strict:
        return False
    return True


def average(values):
    total = 0
    for v in values:
        total += v
    return total / len(values)


def get_name(user):
    return user.get("name", "unknown")


def add(a, b):
    return a + b


def is_adult(age):
    return age >= 18


def last_item(items):
    return items[len(items)]
