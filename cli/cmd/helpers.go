package cmd

import (
	"fmt"
	"os/exec"
	"strings"
)

// FindCircuitPythonDevice looks for a block device with the label "CIRCUITPY"
// Returns the path (e.g. /dev/sda1) or an error if not found.
func FindCircuitPythonDevice() (string, error) {
	out, err := exec.Command("lsblk", "-o", "PATH,LABEL", "-n", "-r").Output()
	if err != nil {
		return "", fmt.Errorf("error executing lsblk: %w", err)
	}

	lines := strings.Split(string(out), "\n")
	for _, line := range lines {
		if strings.Contains(line, "CIRCUITPY") {
			parts := strings.Fields(line)
			if len(parts) > 0 {
				return parts[0], nil
			}
		}
	}

	return "", fmt.Errorf("CIRCUITPY device not found")
}
