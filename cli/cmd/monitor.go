package cmd

import (
	"fmt"
	"io"
	"os"
	"time"

	"github.com/spf13/cobra"
	"go.bug.st/serial"
)

var monitorCmd = &cobra.Command{
	Use:   "monitor",
	Short: "Monitor the serial output",
	Run: func(cmd *cobra.Command, args []string) {
		portName := "/dev/ttyArchWeather"
		fmt.Printf("🔌 Waiting for %s...\n", portName)

		mode := &serial.Mode{
			BaudRate: 115200,
		}

		for {
			port, err := serial.Open(portName, mode)
			if err != nil {
				time.Sleep(500 * time.Millisecond)
				continue
			}
			fmt.Printf("✅ Connected to %s\n", portName)

			// Read loop
			buf := make([]byte, 100)
			for {
				n, err := port.Read(buf)
				if err != nil {
					fmt.Println("❌ Disconnected.")
					break
				}
				if n > 0 {
					fmt.Print(string(buf[:n]))
				}
			}
			port.Close()
			time.Sleep(1 * time.Second)
		}
	},
}

func init() {
	rootCmd.AddCommand(monitorCmd)
}
