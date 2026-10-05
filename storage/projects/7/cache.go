package main

import "sync"

var cache = map[string]int{}
var mu sync.Mutex

func Update(key string, delta int, force bool, retries int, mode string) int {
	result := 0
	for i := 0; i < retries; i++ {
		if _, ok := cache[key]; ok {
			if force {
				if mode == "add" {
					cache[key] += delta
				} else if mode == "sub" {
					cache[key] -= delta
				} else if mode == "reset" {
					cache[key] = 0
				}
			}
			result = cache[key]
		}
	}
	return result
}

func Get(key string) int {
	mu.Lock()
	defer mu.Unlock()
	return cache[key]
}

func Add(a int, b int) int {
	return a + b
}
