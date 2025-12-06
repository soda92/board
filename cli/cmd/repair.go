package cmd

import (
	"fmt"
	"os"
	"os/exec"
	"strings"

	"github.com/spf13/cobra"
)

var repairCmd = &cobra.Command{
	Use:   "repair",
	Short: "Reformat the board filesystem (erases everything!)",
	Run: func(cmd *cobra.Command, args []string) {
		// 1. Find Device
		out, err := exec.Command("lsblk", "-o", "PATH,LABEL", "-n", "-r").Output()
		if err != nil {
			fmt.Println("❌ Error finding devices:", err)
			return
		}

		var devPath string
		lines := strings.Split(string(out), "\n")
		for _, line := range lines {
			if strings.Contains(line, "CIRCUITPY") {
				parts := strings.Fields(line)
				if len(parts) > 0 {
					devPath = parts[0]
					break
				}
			}
		}

		if devPath == "" {
			fmt.Println("❌ Error: CIRCUITPY device not found.")
			return
		}

		fmt.Printf("⚠️  WARNING: This will ERASE ALL DATA on %s\n", devPath)
		fmt.Print("Are you sure? (y/N): ")
		var response string
		fmt.Scanln(&response)
		if strings.ToLower(response) != "y" {
			fmt.Println("Aborted.")
			return
		}

		fmt.Println("🧹 Formatting...")
		formatCmd := exec.Command("sudo", "mkfs.vfat", "-I", "-n", "CIRCUITPY", devPath)
		formatCmd.Stdout = os.Stdout
		formatCmd.Stderr = os.Stderr
		if err := formatCmd.Run(); err != nil {
			fmt.Println("❌ Format failed:", err)
			return
		}

		fmt.Println("✅ Format complete. You should run 'deploy' now.")
	},
}

func init() {
	rootCmd.AddCommand(repairCmd)
}
