package cmd

import (
	"fmt"
	"time"

	"github.com/spf13/cobra"
	"go.bug.st/serial"
)

var (
	monitorPort string
	monitorBaud int
)

var monitorCmd = &cobra.Command{
	Use:   "monitor",
	Short: "Monitor the serial output",
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Printf("🔌 Waiting for %s at %d baud...\n", monitorPort, monitorBaud)

		mode := &serial.Mode{
			BaudRate: monitorBaud,
		}

		for {
			port, err := serial.Open(monitorPort, mode)
			if err != nil {
				time.Sleep(500 * time.Millisecond)
				continue
			}
			fmt.Printf("✅ Connected to %s\n", monitorPort)

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
	monitorCmd.Flags().StringVarP(&monitorPort, "port", "p", DefaultPort, "Serial port to monitor")
	monitorCmd.Flags().IntVarP(&monitorBaud, "baud", "b", DefaultBaud, "Baud rate")
}
