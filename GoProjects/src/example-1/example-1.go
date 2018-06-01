package main

import (
	"fmt"
	"os"
	"os/signal"
	"syscall"
	"time"
)

func main() {
	go Task()
	Start()
}

func Task() {
	fmt.Println("进程启动...")
	var sum = 0
	for {
		sum++
		fmt.Println("sum: ", sum)
		time.Sleep(time.Second)
	}
}

func Start() {
	//创建监听退出chan
	var c = make(chan os.Signal)

	//创建监听退出chan
	signal.Notify(c, syscall.SIGHUP, syscall.SIGINT, syscall.SIGTERM, syscall.SIGQUIT)

	for s := range c {
		switch s {
		case syscall.SIGHUP, syscall.SIGINT, syscall.SIGTERM, syscall.SIGQUIT:
			fmt.Println("退出", s)
			Exitfunc()
		default:
			fmt.Println("other", s)
		}
	}
}

func Exitfunc() {
	fmt.Println("开始退出...")
	fmt.Println("执行清理...")
	fmt.Println("结束退出...")
	os.Exit(0)
}
