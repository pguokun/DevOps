package main

import (
	"fmt"
	"os"
	"os/signal"
	"syscall"
	"time"
)

func Exitfunc() {
	fmt.Println("开始退出...")
	fmt.Println("执行清理...")
	fmt.Println("结束退出...")
	os.Exit(0)
}

func main() {
	//创建监听退出chan
	var c = make(chan os.Signal)
	//监听指定信号 ctrl+c kill
	signal.Notify(c, syscall.SIGHUP, syscall.SIGINT, syscall.SIGTERM, syscall.SIGQUIT)

	go func() {
		for s := range c {
			switch s {
			case syscall.SIGHUP, syscall.SIGINT, syscall.SIGTERM, syscall.SIGQUIT:
				fmt.Println("退出", s)
				Exitfunc()
			default:
				fmt.Println("other", s)
			}
		}
	}()

	fmt.Println("进程启动...")
	var sum = 0
	for {
		sum++
		fmt.Println("sum: ", sum)
		time.Sleep(time.Second)
	}
}
