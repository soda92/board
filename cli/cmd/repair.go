package cmd

import (
	"bufio"
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
		devPath, err := FindCircuitPythonDevice()
		if err != nil {
			fmt.Println("❌ Error:", err)
			return
		}

		fmt.Printf("⚠️  WARNING: This will ERASE ALL DATA on %s\n", devPath)
		fmt.Print("Are you sure? (y/N): ")
		
		reader := bufio.NewReader(os.Stdin)
		response, _ := reader.ReadString('\n')
		response = strings.TrimSpace(response)

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
