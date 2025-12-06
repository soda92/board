package cmd

import (
	"fmt"
	"time"

	"github.com/spf13/cobra"
	"go.bug.st/serial"
)

var (
	reloadPort string
	reloadBaud int
)

var reloadCmd = &cobra.Command{
	Use:   "reload",
	Short: "Trigger a soft reboot (CTRL+D)",
	Run: func(cmd *cobra.Command, args []string) {
		mode := &serial.Mode{
			BaudRate: reloadBaud,
		}

		port, err := serial.Open(reloadPort, mode)
		if err != nil {
			fmt.Printf("❌ Error opening port %s: %v\n", reloadPort, err)
			return
		}
		defer port.Close()

		fmt.Println("🔄 Sending Soft Reboot (Ctrl+D)...")
		
		// Create a channel to signal done reading
		done := make(chan bool)

		// Read output in background
		go func() {
			buf := make([]byte, 100)
			timeout := time.After(5 * time.Second)
			for {
				select {
				case <-timeout:
					done <- true
					return
				default:
					// Set read timeout to avoid blocking forever
					port.SetReadTimeout(100 * time.Millisecond)
					n, err := port.Read(buf)
					if err != nil {
						fmt.Printf("\n❌ Read error: %v\n", err)
						done <- true
						return
					}
					if n > 0 {
						fmt.Print(string(buf[:n]))
					}
				}
			}
		}()

		// Send Ctrl+D
		_, err = port.Write([]byte{0x04})
		if err != nil {
			fmt.Println("❌ Error writing to port:", err)
			return
		}

		<-done
		fmt.Println("\n✅ Done.")
	},
}

func init() {
	rootCmd.AddCommand(reloadCmd)
	reloadCmd.Flags().StringVarP(&reloadPort, "port", "p", DefaultPort, "Serial port")
	reloadCmd.Flags().IntVarP(&reloadBaud, "baud", "b", DefaultBaud, "Baud rate")
}
