"""
Performance Profiler Tool

A comprehensive timing tool for measuring performance across multiple code segments.
Provides detailed reports with timing statistics and nested measurements.

Usage:
    profiler = Profiler()
    
    # Start total measurement
    profiler.start("total")
    
    # Measure specific segments
    with profiler.measure("segment1"):
        # your code here
        pass
    
    # Manual measurement
    profiler.start("segment2")
    # your code here
    profiler.end("segment2")
    
    profiler.end("total")
    
    # Get report
    report = profiler.get_report()
    print(report)
"""

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from contextlib import contextmanager
import threading
import sys
import os


class Colors:
    """ANSI color codes for terminal output."""
    # Text colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    STRIKETHROUGH = '\033[9m'
    
    # Reset
    RESET = '\033[0m'
    END = '\033[0m'


def supports_color() -> bool:
    """Check if the terminal supports color output."""
    # Check if we're in a terminal that supports color
    return (
        hasattr(sys.stderr, "isatty") and sys.stderr.isatty() and
        os.environ.get("TERM") != "dumb" and
        os.environ.get("NO_COLOR") is None
    )


def colorize(text: str, color: str, style: str = "") -> str:
    """Apply color and style to text if terminal supports it."""
    if supports_color():
        return f"{style}{color}{text}{Colors.RESET}"
    return text


def format_performance_level(duration: float, total) -> tuple[str, str]:
    """Return appropriate color and style based on performance level."""
    if total <= 0:
        return Colors.BRIGHT_WHITE, ""
    
    percentage = (duration / total) * 100
    
    if percentage < 1.0:  # < 1% - excellent
        return Colors.BRIGHT_GREEN, ""
    elif percentage < 5.0:  # < 5% - good
        return Colors.GREEN, ""
    elif percentage < 10.0:  # < 10% - okay
        return Colors.YELLOW, ""
    elif percentage < 20.0:  # < 20% - slow
        return Colors.RED, ""
    else:  # > 20% - very slow
        return Colors.BRIGHT_RED, Colors.BOLD


@dataclass
class TimingData:
    """Data structure for storing timing information."""
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    duration: Optional[float] = None
    measurements: List[float] = field(default_factory=list)
    parent: Optional[str] = None
    children: List[str] = field(default_factory=list)
    depth: int = 0


class Profiler:
    """
    A high-performance profiler for measuring code execution times.
    
    Features:
    - Multiple concurrent measurements
    - Nested timing support
    - Context manager support
    - Detailed statistical reports
    - Thread-safe operations
    """
    
    def __init__(self, name: str = "ProfilerSession", use_colors: bool = True):
        self.name = name
        self.timings: Dict[str, TimingData] = {}
        self.active_timers: Dict[str, float] = {}
        self.call_stack: List[str] = []
        self._lock = threading.Lock()
        self.session_start = time.time()
        self.use_colors = use_colors and supports_color()
        
    def start(self, label: str) -> None:
        """Start timing for a labeled segment."""
        with self._lock:
            current_time = time.time()
            
            if label in self.active_timers:
                raise ValueError(f"Timer '{label}' is already active")
            
            # Initialize timing data if not exists
            if label not in self.timings:
                self.timings[label] = TimingData()
                
            # Set parent-child relationships
            if self.call_stack:
                parent = self.call_stack[-1]
                self.timings[label].parent = parent
                if label not in self.timings[parent].children:
                    self.timings[parent].children.append(label)
            
            self.timings[label].depth = len(self.call_stack)
            self.timings[label].start_time = current_time
            self.active_timers[label] = current_time
            self.call_stack.append(label)
    
    def end(self, label: str) -> float:
        """End timing for a labeled segment and return duration."""
        with self._lock:
            current_time = time.time()
            
            if label not in self.active_timers:
                raise ValueError(f"Timer '{label}' is not active")
            
            start_time = self.active_timers.pop(label)
            duration = current_time - start_time
            
            timing_data = self.timings[label]
            timing_data.end_time = current_time
            timing_data.duration = duration
            timing_data.measurements.append(duration)
            
            # Remove from call stack
            if label in self.call_stack:
                self.call_stack.remove(label)
            
            return duration
    
    @contextmanager
    def measure(self, label: str):
        """Context manager for automatic timing."""
        self.start(label)
        try:
            yield
        finally:
            self.end(label)
    
    def mark(self, label: str) -> None:
        """Add a timestamp mark without duration measurement."""
        with self._lock:
            if label not in self.timings:
                self.timings[label] = TimingData()
            
            current_time = time.time()
            self.timings[label].measurements.append(current_time - self.session_start)
    
    def reset(self) -> None:
        """Reset all timing data."""
        with self._lock:
            self.timings.clear()
            self.active_timers.clear()
            self.call_stack.clear()
            self.session_start = time.time()
    
    def get_duration(self, label: str) -> Optional[float]:
        """Get the duration of a specific measurement."""
        return self.timings.get(label, TimingData()).duration
    
    def get_average(self, label: str) -> Optional[float]:
        """Get the average duration for a label with multiple measurements."""
        timing_data = self.timings.get(label)
        if timing_data and timing_data.measurements:
            return sum(timing_data.measurements) / len(timing_data.measurements)
        return None
    
    def get_statistics(self, label: str) -> Dict[str, Any]:
        """Get detailed statistics for a label."""
        timing_data = self.timings.get(label)
        if not timing_data or not timing_data.measurements:
            return {}
        
        measurements = timing_data.measurements
        return {
            'count': len(measurements),
            'total': sum(measurements),
            'average': sum(measurements) / len(measurements),
            'min': min(measurements),
            'max': max(measurements),
            'last': measurements[-1] if measurements else None
        }
    
    def get_report(self, sort_by: str = 'duration', include_children: bool = True, use_colors: bool = None) -> str:
        """
        Generate a comprehensive timing report.
        
        Args:
            sort_by: Sort criteria ('duration', 'average', 'count', 'name')
            include_children: Whether to show nested measurements
            use_colors: Override color usage for this report
        """
        if not self.timings:
            no_data_msg = "No measurements recorded."
            if use_colors is None:
                use_colors = self.use_colors
            if use_colors:
                title = colorize(f"=== {self.name} Profiler Report ===", Colors.BRIGHT_CYAN, Colors.BOLD)
                msg = colorize(no_data_msg, Colors.YELLOW)
                return f"{title}\n{msg}"
            return f"=== {self.name} Profiler Report ===\n{no_data_msg}"
        
        if use_colors is None:
            use_colors = self.use_colors
        
        session_duration = time.time() - self.session_start
        
        # Colorized header
        if use_colors:
            title = colorize(f"=== {self.name} Profiler Report ===", Colors.BRIGHT_CYAN, Colors.BOLD)
            duration_text = colorize(f"Session Duration: {session_duration:.4f}s", Colors.BRIGHT_WHITE)
            count_text = colorize(f"Total Measurements: {len(self.timings)}", Colors.BRIGHT_WHITE)
        else:
            title = f"=== {self.name} Profiler Report ==="
            duration_text = f"Session Duration: {session_duration:.4f}s"
            count_text = f"Total Measurements: {len(self.timings)}"
        
        report = [
            title,
            duration_text,
            count_text,
            ""
        ]
        
        # Get root level measurements (no parent)
        root_measurements = [
            (label, data) for label, data in self.timings.items() 
            if data.parent is None and data.measurements
        ]
        
        # Sort measurements
        if sort_by == 'duration':
            root_measurements.sort(key=lambda x: x[1].duration or 0, reverse=True)
        elif sort_by == 'average':
            root_measurements.sort(key=lambda x: sum(x[1].measurements) / len(x[1].measurements) if x[1].measurements else 0, reverse=True)
        elif sort_by == 'count':
            root_measurements.sort(key=lambda x: len(x[1].measurements), reverse=True)
        elif sort_by == 'name':
            root_measurements.sort(key=lambda x: x[0])
        
        def format_duration(duration: float,  total: float, colored: bool = True) -> str:
            """Format duration in appropriate units with optional colors."""
            if duration >= 1.0:
                formatted = f"{duration:.4f}s"
            elif duration >= 0.001:
                formatted = f"{duration * 1000:.2f}ms"
            else:
                formatted = f"{duration * 1000000:.1f}μs"
            
            if colored and use_colors:
                color, style = format_performance_level(duration, total)
                return colorize(formatted, color, style)
            return formatted
        
        def add_measurement_to_report(label: str, data: TimingData, indent: int = 0):
            """Recursively add measurements to report."""
            if not data.measurements:
                return
            
            prefix = "  " * indent
            stats = self.get_statistics(label)
            
            # Color the label based on depth
            if use_colors:
                depth_colors = [Colors.BRIGHT_WHITE, Colors.BRIGHT_BLUE, Colors.BRIGHT_MAGENTA, 
                               Colors.BRIGHT_YELLOW, Colors.BRIGHT_GREEN, Colors.BRIGHT_CYAN]
                label_color = depth_colors[min(indent, len(depth_colors) - 1)]
                colored_label = colorize(label, label_color, Colors.BOLD if indent == 0 else "")
            else:
                colored_label = label
            
            if stats['count'] == 1:
                duration_str = format_duration(stats['last'], stats['total'], use_colors)
                report.append(f"{prefix}{colored_label}: {duration_str}")
            else:
                avg_str = format_duration(stats['average'], stats['total'], use_colors)
                total_str = format_duration(stats['total'], session_duration, use_colors)
                min_str = format_duration(stats['min'], stats['total'], use_colors)
                max_str = format_duration(stats['max'], stats['total'], use_colors)

                if use_colors:
                    count_str = colorize(str(stats['count']), Colors.BRIGHT_WHITE)
                else:
                    count_str = str(stats['count'])
                
                report.append(
                    f"{prefix}{colored_label}: avg={avg_str}, "
                    f"total={total_str}, "
                    f"count={count_str}, "
                    # f"min={min_str}, "
                    # f"max={max_str}"
                )
            
            # Add percentage of parent if applicable
            if data.parent and data.parent in self.timings:
                parent_stats = self.get_statistics(data.parent)
                if parent_stats.get('total', 0) > 0:
                    percentage = (stats['total'] / parent_stats['total']) * 100
                    if use_colors:
                        # Color percentage based on how much of parent it takes
                        if percentage > 70:
                            perc_color = Colors.BRIGHT_RED
                        elif percentage > 40:
                            perc_color = Colors.YELLOW
                        else:
                            perc_color = Colors.GREEN
                        percentage_str = colorize(f"({percentage:.1f}% of {data.parent})", perc_color)
                    else:
                        percentage_str = f"({percentage:.1f}% of {data.parent})"
                    report[-1] += f" {percentage_str}"
            
            # Add children recursively
            if include_children and data.children:
                for child_label in data.children:
                    if child_label in self.timings:
                        add_measurement_to_report(child_label, self.timings[child_label], indent + 1)
        
        # Add all measurements to report
        for label, data in root_measurements:
            add_measurement_to_report(label, data)
        
        # Add summary statistics
        total_measured_time = sum(
            sum(data.measurements) for data in self.timings.values() 
            if data.measurements and data.parent is None
        )
        
        if total_measured_time > 0:
            coverage_pct = (total_measured_time / session_duration) * 100
            
            if use_colors:
                summary_title = colorize("=== Summary ===", Colors.BRIGHT_CYAN, Colors.BOLD)
                measured_time_str = format_duration(total_measured_time, total_measured_time, use_colors)
                overhead_str = format_duration(session_duration - total_measured_time, session_duration, use_colors)

                # Color coverage based on percentage
                if coverage_pct > 90:
                    coverage_color = Colors.BRIGHT_GREEN
                elif coverage_pct > 70:
                    coverage_color = Colors.GREEN
                elif coverage_pct > 50:
                    coverage_color = Colors.YELLOW
                else:
                    coverage_color = Colors.RED
                coverage_str = colorize(f"{coverage_pct:.1f}%", coverage_color)
            else:
                summary_title = "=== Summary ==="
                measured_time_str = format_duration(total_measured_time, total_measured_time, False)
                overhead_str = format_duration(session_duration - total_measured_time, session_duration, False)
                coverage_str = f"{coverage_pct:.1f}%"
            
            report.extend([
                "",
                summary_title,
                f"Total Measured Time: {measured_time_str}",
                f"Measurement Overhead: {overhead_str}",
                f"Coverage: {coverage_str}"
            ])
        
        return "\n".join(report)
    
    def export_csv(self, filename: str) -> None:
        """Export timing data to CSV file."""
        import csv
        
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['label', 'parent', 'depth', 'count', 'total', 'average', 'min', 'max', 'last']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for label, data in self.timings.items():
                if data.measurements:
                    stats = self.get_statistics(label)
                    writer.writerow({
                        'label': label,
                        'parent': data.parent or '',
                        'depth': data.depth,
                        'count': stats['count'],
                        'total': stats['total'],
                        'average': stats['average'],
                        'min': stats['min'],
                        'max': stats['max'],
                        'last': stats['last']
                    })


# Global profiler instance for convenience
_global_profiler = Profiler("Global", use_colors=True)

def start(label: str) -> None:
    """Convenience function to start timing with global profiler."""
    _global_profiler.start(label)

def end(label: str) -> float:
    """Convenience function to end timing with global profiler."""
    return _global_profiler.end(label)

def measure(label: str):
    """Convenience function to get context manager with global profiler."""
    return _global_profiler.measure(label)

def mark(label: str) -> None:
    """Convenience function to add mark with global profiler."""
    _global_profiler.mark(label)

def get_report(sort_by: str = 'duration', use_colors: bool = None) -> str:
    """Convenience function to get report from global profiler."""
    return _global_profiler.get_report(sort_by, use_colors=use_colors)

def reset() -> None:
    """Convenience function to reset global profiler."""
    _global_profiler.reset()