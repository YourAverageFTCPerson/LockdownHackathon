package average.ftc.lockdown;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.*;
import java.util.function.Supplier;

public class ServerSide {
    private static double square(double x) {
        return x * x;
    }

    public record Position(double x, double y, double orientation) {
        public static Position parse(String asString) {
            String[] values = asString.split(",");
            return new Position(Double.parseDouble(values[0]), Double.parseDouble(values[1]), Double.parseDouble(values[2]));
        }

        public static double SUSPICIOUS_MOVEMENT = Double.POSITIVE_INFINITY;

        public double distance(Position other) {
            return Math.sqrt(square((Objects.requireNonNull(other).x) - this.x) + square(other.y - this.y));
        }

        public double distance(double x, double y) {
            return Math.sqrt(square(x - this.x) + square(y - this.y));
        }
    }

    private static final Position SPAWN = new Position(0, 0, 0);

    public record Circle(double size, Position relativeLocation) {
    }

    // In metres

    public static final double MINIMUM_HEIGHT = -100;
    public static final double MAXIMUM_HEIGHT = 201; // >= 300 is mountain height

    public static final double MOUNTAIN_WIDTH = 1000;

    public record Mountain(Position position, Circle[] circle) {
    }

    public static LinkedList<Mountain> mountains = new LinkedList<>();

    public static final float ROUGHNESS = 0.63f;

    public static final int ITERATIONS = 20;

    public static class Square {
        int p1, p2, p3, p4;

        public Square(int p1, int p2, int p3, int p4) {
            this.p1 = p1;
            this.p2 = p2;
            this.p3 = p3;
            this.p4 = p4;
        }
    }
    public static class Vector3 {
        public float y;
        public Float x, z; // May be null

        public Vector3() {
        }
    }

    public static float randomRange(float min, float max) {
        return (float) (min + (Math.random() * (max - min)));
    }

    public static Square[] splitSquare(Square square, Vector3[] points, float r, int i) {
        int p1 = square.p1;
        int p2 = square.p2;
        int p3 = square.p3;
        int p4 = square.p4;
        int p5 = (p1+p4)/2;
        float perturbation = (float) Math.pow(r, i);
        points[p5].y = (points[p1].y + points[p2].y + points[p3].y + points[p4].y)/4 + randomRange(-perturbation, perturbation);
        int p6 = (p1+p3)/2;
        int p7 = (p3+p4)/2;
        int p8 = (p4+p2)/2;
        int p9 = (p2+p1)/2;
        points[p6].y = assign_proper_value(p6, p1, p3, p5, points, perturbation);
        points[p7].y = assign_proper_value(p7, p3, p4, p5, points, perturbation);
        points[p8].y = assign_proper_value(p8, p4, p2, p5, points, perturbation);
        points[p9].y = assign_proper_value(p9, p2, p1, p5, points, perturbation);

        Square[] tab = new Square[4];
        tab[0] = new Square(p1, p9, p6, p5);
        tab[1] = new Square(p6, p5, p3, p7);
        tab[2] = new Square(p9, p2, p5, p8);
        tab[3] = new Square(p5, p8, p7, p4);
        return tab;
    }

    private static float mean_diamond(int p1, int p2, int p3, Vector3[] points) {
        return (points[p1].y + points[p2].y + points[p3].y)/3;
    }

    private static float assign_proper_value(int p, int p1, int p2, int p3, Vector3[] points, float perturbation) {
        if(points[p].y == 0) {
            return mean_diamond(p1, p2, p3, points) + randomRange(-perturbation, perturbation);
        }
        return (points[p].y * 3 + points[p3].y + randomRange(-perturbation, perturbation))/4;
    }

    public static int pow(int a, int b) {
        assert a > 0 && b > 0;
        int result = a;
        for (int i = 0; i < b; i++) {
            result *= a;
        }
        return result;
    }

    public static final int AMOUNT = pow(4, ITERATIONS);

    public static Circle[] generateMountain(Position origin) { // Diamond-Square algo
        Vector3[] points = new Vector3[AMOUNT];
        Arrays.fill(points, new Vector3());

        LinkedList<Square> squares = new LinkedList<>(List.of(new Square(0, 0, AMOUNT - 1, AMOUNT - 1)));

        for (int i = 0; i < ITERATIONS; i++) {
            LinkedList<Square> temp = new LinkedList<>();
            int finalI = i;
            squares.forEach(s -> {
                synchronized (temp) {
                    temp.addAll(List.of(splitSquare(s, points, ROUGHNESS, finalI)));
                }
            });
            squares = temp;
        }

        return null;
    }

    public static final LinkedList<Player> players = new LinkedList<>();

    public static final float MAX_ABS_X = 30_000_000, MAX_ABS_Y = MAX_ABS_X;


    public static final LinkedList<Position> EXISTING_MOUNTAINS = new LinkedList<>();

    private static final int BUFLEN = 128;

    private static String padString(String string) {
        assert string.length() <= BUFLEN;

        return string + " ".repeat(BUFLEN - string.length());
    }


    public static class Player {
        public String sendify() {
            return position.x() + "," + position.y() + "," + position.orientation();
        }

        public Socket socket;

        public String username;
//
        public Position position;

        public final Object positionLock = new Object();

        private final PrintWriter writer;

        @Override
        public String toString() {
            return "Player{" +
                    ", username='" + username + '\'' +
                    ", position=" + position +
                    '}';
        }

        public Player(Socket socket, String username, Supplier<Position> supplier) {
            this.socket = Objects.requireNonNull(socket);
            this.username = username;
            try {
                this.writer = new PrintWriter(socket.getOutputStream());
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
            this.position = new Position(0, 0, 0);
            synchronized (players) {
                players.add(this);
            }
            System.out.println("1 hr");
            new Thread(() -> {
                Position previous = SPAWN;

                Position hypothetical;

                try {
                    while (true) {
                        hypothetical = supplier.get();
                        if (hypothetical.distance(previous) >= Position.SUSPICIOUS_MOVEMENT) {
                            throw new Error();
                        }
                        synchronized (positionLock) {
                            this.position = hypothetical;
                        }
                        previous = hypothetical;
                    }
                } catch (Exception e) {
                    throw new RuntimeException(e);
                }
            }).start();
            new Thread(() -> {
                while (true) {
                    synchronized (players) {
                        Iterator<Player> it = players.iterator();
                        for (int i = 0; i < players.size(); i++) {
                            assert it.hasNext();
                            Player next = it.next();
                            if (next.username.equals(username)) continue;
                            System.out.println(Player.this.position.distance(next.position));
                            if (Player.this.position.distance(next.position) <= 5000) {
                                System.out.println("Success");
                                writer.print(padString(next.sendify() + " "));
                            }
                        }
                    }
                    writer.flush();
//                    try {
//                        Thread.sleep(1);
//                    } catch (InterruptedException e) {
//                        throw new RuntimeException(e);
//                    }
                }
            }).start();
            new Thread(() -> { // Mountain generation

            }).start();
        }
    }


    public static void processConnection(Socket socket) {
        try {
            BufferedReader reader = new BufferedReader(new InputStreamReader(socket.getInputStream()));

            String username = reader.readLine();
            new Player(socket, username, (() -> {
                try {
                    return Position.parse(reader.readLine());
                } catch (IOException e) {
                    throw new RuntimeException(e);
                }
            }));
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    public static void main(String[] args) throws Exception {
        try (ServerSocket serverSocket = new ServerSocket(5008)) {
            while (true) {
                processConnection(serverSocket.accept());
            }
        }
    }
}
